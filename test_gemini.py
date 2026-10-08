from services.gemini_service import describe_scene

image_path = "uploads/kitchen.avif"

description = describe_scene(image_path)

print("\nScene Description:\n")
print(description)