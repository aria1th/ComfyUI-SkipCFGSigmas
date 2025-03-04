

try:
    from comfy.model_patcher import ModelPatcher

    # #BACKEND = "ComfyUI"
except ImportError:
    try:
        from ldm_patched.modules.model_patcher import ModelPatcher

        # #BACKEND = "reForge"
    except ImportError:
        from backend.patcher.base import ModelPatcher

        # #BACKEND = "Forge"

class CFGControl_SKIPCFG:
    """
    Skip the CFG Control node.
    Refer to comfy\samplers.py
    rescale_strength: 0.0 to 1.0, default 0,
    sigma range >25 might be beneficial to skip
    """
    #{"denoised": cfg_result, "cond": cond, "uncond": uncond, "model": model, "uncond_denoised": uncond_pred, "cond_denoised": cond_pred,
    #            "sigma": timestep, "model_options": model_options, "input": x}
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("MODEL",),
                "sigma_min": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1000.0, "step": 0.001, "round": 0.001}),
                "sigma_max": ("FLOAT", {"default": 1000.0, "min": 0.0, "max": 1000.0, "step": 0.001, "round": 0.001}),
                "rescale_strength": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.1, "round": 0.01}),
            },
        }

    RETURN_TYPES = ("MODEL",)
    FUNCTION = "patch"

    CATEGORY = "model_patches/unet"

    def patch(self, model: ModelPatcher, sigma_min:int, sigma_max:int, rescale_strength:0.0):
        def skip_cfg(args):
            denoised = args["denoised"]
            if sigma_min <= args["sigma"] <= sigma_max:
                #print(f"sampling timestep {args['sigma']} skipped")
                return denoised # default
            else:
                #print(f"sampling timestep {args['sigma']} passed")
                if rescale_strength > 0:
                    cond_denoise_diff = args["denoised"] - args["cond_denoised"]
                    pred = args["cond_denoised"] + rescale_strength * cond_denoise_diff
                else:
                    pred = args["cond_denoised"] # ignore uncond
                return pred
        m = model.clone()
        m.set_model_sampler_post_cfg_function(skip_cfg)
        return (m,)

NODE_CLASS_MAPPINGS = {
    "CFGControl_SKIPCFG": CFGControl_SKIPCFG,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CFGControl_SKIPCFG": "CFGControl_SKIPCFG",
}
