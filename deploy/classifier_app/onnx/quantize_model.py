GLUE_TASKS = ["cola", "mnli", "mnli-mm", "mrpc", "qnli", "qqp", "rte", "sst2", "stsb", "wnli"]
task = "sst2"
model_checkpoint = "distilbert-base-uncased-finetuned-sst-2-english"
batch_size = 8



QUANTIZATION_APPROACH = ["dynamic", "static"]

quantization_approach = "static"



per_channel = True
weight_type = "uint8"
max_calib_samples = 40
op_types_to_quantize = ["MatMul", "Mul", "Reshape", "Gather", "Transpose"]



from datasets import load_dataset, load_metric

actual_task = "mnli" if task == "mnli-mm" else task
dataset = load_dataset("glue", actual_task)
metric = load_metric("glue", actual_task)



from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

task_to_keys = {
    "cola": ("sentence", None),
    "mnli": ("premise", "hypothesis"),
    "mnli-mm": ("premise", "hypothesis"),
    "mrpc": ("sentence1", "sentence2"),
    "qnli": ("question", "sentence"),
    "qqp": ("question1", "question2"),
    "rte": ("sentence1", "sentence2"),
    "sst2": ("sentence", None),
    "stsb": ("sentence1", "sentence2"),
    "wnli": ("sentence1", "sentence2"),
}



sentence1_key, sentence2_key = task_to_keys[task]
max_seq_length = min(128, tokenizer.model_max_length)
padding = "max_length"

def preprocess_function(examples):
    args = (
        (examples[sentence1_key],) if sentence2_key is None else (examples[sentence1_key], examples[sentence2_key])
    )
    return tokenizer(*args, padding=padding, max_length=max_seq_length, truncation=True)

encoded_dataset = dataset.map(preprocess_function, batched=True)

from optimum.onnxruntime import ORTConfig, ORTModel, ORTQuantizer

ort_config = ORTConfig(
    quantization_approach=quantization_approach,
    per_channel=per_channel,
    weight_type=weight_type,
    activation_type="uint8",
    max_samples=max_calib_samples,
    calib_batch_size=batch_size,
    op_types_to_quantize=op_types_to_quantize,
)

import os

model_name = model_checkpoint.split("/")[-1]
output_dir = f"{model_name}-finetuned-{task}"
os.makedirs(output_dir, exist_ok=True)

calib_dataset = encoded_dataset["train"].select(range(max_calib_samples)) if quantization_approach == "static" else None
quantizer = ORTQuantizer(ort_config, calib_dataset=calib_dataset)
quantizer.fit(model_checkpoint, output_dir, feature="sequence-classification")



import numpy as np

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    if task != "stsb":
        predictions = np.argmax(predictions, axis=1)
    else:
        predictions = predictions[:, 0]
    return metric.compute(predictions=predictions, references=labels)

metric_name = "pearson" if task == "stsb" else "matthews_correlation" if task == "cola" else "accuracy"

from torch.utils.data import DataLoader
from transformers import default_data_collator

model_path = os.path.join(output_dir, "model.onnx")
q8_model_path = os.path.join(output_dir, "model-quantized.onnx")
onnx_config = quantizer.onnx_config
validation_key = "validation_mismatched" if task == "mnli-mm" else "validation_matched" if task == "mnli" else "validation"
eval_dataset = encoded_dataset[validation_key]
eval_dataloader = DataLoader(eval_dataset, batch_size=batch_size, collate_fn=default_data_collator)

q8_ort_model = ORTModel(q8_model_path, onnx_config, compute_metrics=compute_metrics)
q8_model_output = q8_ort_model.evaluation_loop(eval_dataloader)
q8_model_result = q8_model_output.metrics.get(metric_name)

ort_model = ORTModel(model_path, onnx_config, compute_metrics=compute_metrics)
model_output = ort_model.evaluation_loop(eval_dataloader)
fp_model_result = model_output.metrics.get(metric_name)

ort_config.save_pretrained(output_dir)

print(f"Optimized model with {metric_name} of {round(q8_model_result * 100, 2)} saved to: {q8_model_path}.")
print(
    f"This results in a drop of {round((fp_model_result - q8_model_result) * 100, 2)} in {metric_name} when"
    f" compared to the full-precision model which has an {metric_name} of {round(fp_model_result * 100, 2)}."
)



fp_model_size = os.path.getsize(model_path) / (1024*1024)
q_model_size = os.path.getsize(q8_model_path) / (1024*1024)

print(f"The full-precision model size is {round(fp_model_size)} MB while the quantized model one is {round(q_model_size)} MB.")
print(f"The resulting quantized model is {round(fp_model_size / q_model_size, 2)}x smaller than the full-precision one.")


