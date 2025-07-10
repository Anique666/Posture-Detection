import cv2
import mediapipe as mp
import math
import os

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

def calculate_angle(p1, p2, p3):
    v1 = (p1.x - p2.x, p1.y - p2.y)
    v2 = (p3.x - p2.x, p3.y - p2.y)
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
    mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
    if mag1 == 0 or mag2 == 0:
        return 0
    angle = math.acos(dot / (mag1 * mag2))
    return math.degrees(angle)

def classify_posture(landmarks):
    rs = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    ls = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    rh = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    lh = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    rk = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
    lk = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    ra = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
    la = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]

    avg_s_y = (rs.y + ls.y) / 2
    avg_h_y = (rh.y + lh.y) / 2
    avg_k_y = (rk.y + lk.y) / 2

    r_k_a = calculate_angle(rh, rk, ra)
    l_k_a = calculate_angle(lh, lk, la)
    a_k_a = (r_k_a + l_k_a) / 2

    # New Rule: Filter out standing postures
    vertical_alignment = abs(avg_s_y - avg_h_y) < 0.05 and abs(avg_h_y - avg_k_y) < 0.05
    if vertical_alignment:
        return "Other"

    if avg_s_y < avg_h_y < avg_k_y:
        if a_k_a < 150:
            return "Squatting"
        elif a_k_a >= 150:
            return "Sitting"

    return "Other"


def run_pose_model(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(3))
    height = int(cap.get(4))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Re-encode for browser compatibility
    fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 encoding
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    counts = {"Sitting": 0, "Squatting": 0, "Other": 0}

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(rgb)

        feedback = "No Pose Detected"
        if result.pose_landmarks:
            mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            posture = classify_posture(result.pose_landmarks.landmark)
            counts[posture] += 1
            feedback = f"{posture} Posture"

        cv2.putText(frame, feedback, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        out.write(frame)

    cap.release()
    out.release()

    dominant = max(counts, key=counts.get)
    return dominant, f"Most frames were classified as {dominant.lower()}."
