from ultralytics import YOLO
import cv2

# Load model
model = YOLO("yolov8n.pt")   # Change to yolov8s.pt if you have it

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

print("Press Q to quit")

while True:

    ret, frame = cap.read()

    if not ret:
        break

    results = model(frame)

    annotated = results[0].plot()

    print("\nDetected Objects:")

    for box in results[0].boxes:

        confidence = float(box.conf[0])

        if confidence < 0.5:
            continue

        class_id = int(box.cls[0])

        name = model.names[class_id]

        print(
            f"{name} ({confidence:.2f})"
        )

    cv2.imshow("YOLO Test", annotated)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()