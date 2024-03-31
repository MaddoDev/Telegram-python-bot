from ctransformers import AutoModelForCausalLM

llm = AutoModelForCausalLM.from_pretrained("/path/to/ggml-model.bin", model_type="gpt2")

print(llm("AI is going to"))