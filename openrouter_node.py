import base64
import json
import requests
from PIL import Image
import io
import torch
from torchvision.transforms import ToPILImage

class OpenrouterNode:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_url": ("STRING", {
                    "multiline": False,
                    "default": "https://openrouter.ai/api/v1/chat/completions"
                }),
                "model": ("STRING", {
                    "multiline": False,
                    "default": "gpt4o"
                }),
                "api_key": ("STRING", {
                    "multiline": False,
                    "default": ""
                }),
                "system_prompt": ("STRING", {
                    "multiline": True,
                    "default": "A world without prompts"
                }),
                "user_prompt": ("STRING", {
                    "multiline": True,
                    "default": "A world without prompts"
                }),
                "image_input": ("IMAGE", {
                    "optional": True
                }),
                "temperature": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "round": 2
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_completion"
    CATEGORY = "OpenRouter"

    def get_completion(self, base_url, model, api_key, system_prompt, user_prompt, temperature):
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # Initialize messages with proper structure
            messages = [{
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": system_prompt
                    }
                ],
                
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    }
                ],
                
            }]

            body = {
                "model": model,
                "messages": messages,
                "temperature": temperature
            }

            response = requests.post(base_url, headers=headers, data=json.dumps(body), timeout=120)
            response.raise_for_status()

            response_json = response.json()

            if "choices" in response_json and len(response_json["choices"]) > 0:
                assistant_message = response_json["choices"][0].get("message", {}).get("content", "")
                return (assistant_message,)
            else:
                return ("No response from the model.",)

        except requests.exceptions.RequestException as req_err:
            return (f"Request Error: {str(req_err)}",)
        except Exception as e:
            return (f"Error: {str(e)}",)

class OpenrouterNodeImage:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_url": ("STRING", {
                    "multiline": False,
                    "default": "https://openrouter.ai/api/v1/chat/completions"
                }),
                "model": ("STRING", {
                    "multiline": False,
                    "default": "gpt4o"
                }),
                "api_key": ("STRING", {
                    "multiline": False,
                    "default": ""
                }),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "A world without prompts"
                }),
                "image_input": ("IMAGE", {
                    "optional": True
                }),
                "temperature": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "round": 2
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_completion"
    CATEGORY = "OpenRouter"

    def get_completion(self, base_url, model, api_key, prompt, image_input, temperature):
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # Initialize messages with proper structure
            messages = [{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }]

            if image_input is not None:
                if isinstance(image_input, torch.Tensor):
                    # Handle 4D tensors by removing the batch dimension
                    if image_input.dim() == 4:
                        image_input = image_input.squeeze(0)
                    if image_input.dim() != 3:
                        return ("Error: Image tensor must be 3D after squeezing.",)
                    # Rearrange tensor from [H, W, C] to [C, H, W] if necessary
                    if image_input.shape[-1] in [1, 3, 4]:
                        image_input = image_input.permute(2, 0, 1)
                    else:
                        return (f"Error: Invalid number of channels: {image_input.shape[-1]}.",)
                    to_pil = ToPILImage()
                    pil_image = to_pil(image_input)
                elif isinstance(image_input, Image.Image):
                    pil_image = image_input
                else:
                    return ("Error: Unsupported image_input type.",)

                # Save the image without resizing or cropping
                buffered = io.BytesIO()
                # Handle different Pillow versions for resampling filters
                resample_filter = getattr(Image, "Resampling", None)
                if resample_filter and hasattr(resample_filter, "LANCZOS"):
                    pil_image.save(buffered, format="PNG", resample=Image.Resampling.LANCZOS)
                else:
                    pil_image.save(buffered, format="PNG", resample=Image.LANCZOS)
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                image_data = f"data:image/png;base64,{img_str}"

                image_message = {
                    "type": "image_url",
                    "image_url": {
                        "url": image_data
                    }
                }
                
                # Append the image message to the content list
                messages[0]["content"].append(image_message)

            body = {
                "model": model,
                "messages": messages,
                "temperature": temperature
            }

            response = requests.post(base_url, headers=headers, data=json.dumps(body), timeout=120)
            response.raise_for_status()

            response_json = response.json()

            if "choices" in response_json and len(response_json["choices"]) > 0:
                assistant_message = response_json["choices"][0].get("message", {}).get("content", "")
                return (assistant_message,)
            else:
                return ("No response from the model.",)

        except requests.exceptions.RequestException as req_err:
            return (f"Request Error: {str(req_err)}",)
        except Exception as e:
            return (f"Error: {str(e)}",)

# Node registration
NODE_CLASS_MAPPINGS = {
    "OpenrouterNode": OpenrouterNode,
    "OpenrouterNodeImage": OpenrouterNodeImage
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OpenrouterNodeImage": "OpenRouter Node with Image"
}
