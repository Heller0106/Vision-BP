import cv2
import numpy as np

print("OpenCV versie:", cv2.__version__)
print("Probeer webcam te openen...")

# Probeer verschillende backends en camera indices
import time
cap = None
working_index = -1

for index in [0, 1, 2]:
    print(f"\nProbeer camera index {index}...")
    test_cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    time.sleep(1)
    
    if test_cap.isOpened():
        # Probeer een frame te lezen
        ret, test_frame = test_cap.read()
        if ret and test_frame is not None:
            print(f"  ✓ Camera {index} werkt! Frame grootte: {test_frame.shape}")
            cap = test_cap
            working_index = index
            break
        else:
            print(f"  ✗ Camera {index} is open maar geeft geen beeld")
            test_cap.release()
    else:
        print(f"  ✗ Camera {index} kan niet worden geopend")
        test_cap.release()

if cap is None or not cap.isOpened():
    print("\nError: Geen werkende webcam gevonden")
    print("Controleer of:")
    print("1. Je webcam is aangesloten")
    print("2. Geen andere applicatie de webcam gebruikt")
    print("3. Je webcam toestemming heeft in Windows instellingen")
    print("4. De webcam drivers zijn geïnstalleerd")
    input("Druk op Enter om af te sluiten...")
    exit()

# Stel camera instellingen in voor betere prestaties
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# Probeer auto-exposure en brightness in te schakelen
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)  # Auto exposure
cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)
cap.set(cv2.CAP_PROP_CONTRAST, 0.5)
cap.set(cv2.CAP_PROP_SATURATION, 0.5)
cap.set(cv2.CAP_PROP_GAIN, 0)

# Lees een paar dummy frames om de camera warm te laten draaien
#kjkjj
print(f"\nWebcam {working_index} succesvol geopend!")
print("Warming up camera (dit kan 3-5 seconden duren)...")
for i in range(30):  # Meer frames voor auto-exposure
    ret, warm_frame = cap.read()
    if i % 10 == 0 and ret and warm_frame is not None:
        print(f"  Warmup frame {i}: brightness mean = {warm_frame.mean():.1f}")
    time.sleep(0.1)

print(f"Resolutie: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
print(f"FPS: {int(cap.get(cv2.CAP_PROP_FPS))}")

print("Druk op 'q' om af te sluiten")
print("Druk op 'g' voor grijswaarden")
print("Druk op 'c' voor kleur")
print("Druk op 'e' voor edge detection")
print("Druk op 'b' voor blur effect")
print("Druk op 's' om een screenshot op te slaan")

mode = 'color'  # Standaard modus

frame_count = 0
error_count = 0
while True:
    # Lees een frame van de webcam
    ret, frame = cap.read()
    
    if not ret or frame is None:
        error_count += 1
        print(f"Error: Kan geen frame lezen (fout {error_count})")
        if error_count > 10:
            print("Te veel mislukte pogingen, programma wordt afgesloten")
            break
        time.sleep(0.1)
        continue
    
    # Reset error counter bij succesvol frame
    error_count = 0
    frame_count += 1
    
    # Debug info voor eerste frames
    if frame_count <= 3:
        print(f"Frame {frame_count} ontvangen: {frame.shape}, min={frame.min()}, max={frame.max()}, mean={frame.mean():.1f}")
    
    # Verwerk het frame op basis van de geselecteerde modus
    if mode == 'gray':
        # Converteer naar grijswaarden
        processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_GRAY2BGR)
        label = "Grijswaarden"
        
    elif mode == 'edge':
        # Edge detection met Canny
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        processed_frame = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        label = "Edge Detection"
        
    elif mode == 'blur':
        # Blur effect
        processed_frame = cv2.GaussianBlur(frame, (15, 15), 0)
        label = "Blur Effect"
        
    else:  # color
        processed_frame = frame.copy()
        label = "Origineel"
    
    # Voeg label toe aan het frame
    cv2.putText(processed_frame, label, (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Voeg FPS informatie toe
    cv2.putText(processed_frame, f"Resolutie: {frame.shape[1]}x{frame.shape[0]}", 
                (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # Toon het frame
    cv2.imshow('OpenCV Webcam Analyse', processed_frame)
    
    # Wacht op toetsaanslag
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        # Stop de applicatie
        break
    elif key == ord('g'):
        # Schakel naar grijswaarden modus
        mode = 'gray'
        print("Modus: Grijswaarden")
    elif key == ord('c'):
        # Schakel naar kleur modus
        mode = 'color'
        print("Modus: Kleur")
    elif key == ord('e'):
        # Schakel naar edge detection modus
        mode = 'edge'
        print("Modus: Edge Detection")
    elif key == ord('b'):
        # Schakel naar blur modus
        mode = 'blur'
        print("Modus: Blur")
    elif key == ord('s'):
        # Sla een screenshot op
        filename = f"screenshot_{np.random.randint(1000, 9999)}.jpg"
        cv2.imwrite(filename, processed_frame)
        print(f"Screenshot opgeslagen als: {filename}")

# Maak de webcam vrij en sluit alle vensters
cap.release()
cv2.destroyAllWindows()
print("Webcam gestopt")