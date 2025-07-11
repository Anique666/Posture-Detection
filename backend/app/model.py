import cv2
import mediapipe as mp
import math
from collections import defaultdict


mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

def calculate_angle(p1, p2, p3):
    
    v1 = (p1.x - p2.x, p1.y - p2.y)
    v2 = (p3.x - p2.x, p3.y - p2.y)
    
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
    mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
    
    if mag1 == 0 or mag2 == 0:
        return 0
    
    cos_theta = dot / (mag1 * mag2)
    cos_theta = max(-1.0, min(1.0, cos_theta))
    angle = math.acos(cos_theta)
    return math.degrees(angle)

def calculate_torso_angle(landmarks):
    
    ls = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    rs = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    lh = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    rh = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    
    avg_shoulder_x = (ls.x + rs.x) / 2
    avg_shoulder_y = (ls.y + rs.y) / 2
    avg_hip_x = (lh.x + rh.x) / 2
    avg_hip_y = (lh.y + rh.y) / 2
    
    torso_vector = (avg_shoulder_x - avg_hip_x, avg_shoulder_y - avg_hip_y)
    vertical_vector = (0, -1)
    
    magnitude_torso = (torso_vector[0] ** 2 + torso_vector[1] ** 2) ** 0.5
    if magnitude_torso == 0:
        return None
    
    dot_product = torso_vector[0] * vertical_vector[0] + torso_vector[1] * vertical_vector[1]
    cos_theta = dot_product / magnitude_torso
    cos_theta = max(-1.0, min(1.0, cos_theta))
    angle = math.degrees(math.acos(cos_theta))
    
    return 180 - angle

def classify_posture(landmarks):
    
    rh = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    lh = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    rk = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
    lk = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    ra = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
    la = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    
    r_k_a = calculate_angle(rh, rk, ra)
    l_k_a = calculate_angle(lh, lk, la)
    a_k_a = (r_k_a + l_k_a) / 2
    
    if a_k_a > 170:
        return "Other"  
    elif a_k_a >= 150:
        return "Sitting"
    else:
        return "Squatting"

def check_squatting_posture(landmarks):
    
    rk = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
    lk = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    ra = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
    la = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    
    back_angle = calculate_torso_angle(landmarks)
    
    
    if (rk.x > ra.x or lk.x > la.x) or (back_angle is not None and back_angle < 140):
        return "Incorrect"
    return "Correct"

def check_sitting_posture(landmarks):
    
    rs = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    ls = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    rh = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    lh = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    re = landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value]
    le = landmarks[mp_pose.PoseLandmark.LEFT_EAR.value]
    
    right_neck_angle = calculate_angle(rs, rh, re)
    left_neck_angle = calculate_angle(ls, lh, le)
    neck_angle = (right_neck_angle + left_neck_angle) / 2
    
    back_angle = calculate_torso_angle(landmarks)
    
    
    if (neck_angle > 30) or (back_angle is not None and abs(back_angle - 180) > 30):
        return "Incorrect"
    return "Correct"

def run_pose_model(input_path, output_path):
    
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(3))
    height = int(cap.get(4))
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    counts = defaultdict(int)
    correct_counts = defaultdict(int)
    
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
            
            if posture == "Squatting":
                correctness = check_squatting_posture(result.pose_landmarks.landmark)
            elif posture == "Sitting":
                correctness = check_sitting_posture(result.pose_landmarks.landmark)
            else:  
                correctness = "Other"
            
            if correctness == "Correct":
                correct_counts[posture] += 1
            
            feedback = f"{correctness} {posture}"
        
        cv2.putText(frame, feedback, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        out.write(frame)
    
    cap.release()
    out.release()
    
    
    valid_postures = {k: v for k, v in counts.items() if k != "Other"}
    
    if not valid_postures:
        return "Sitting", "Incorrect"  
    dominant = max(valid_postures, key=valid_postures.get)
    total = counts[dominant]
    correct = correct_counts[dominant]
    
    overall = "Correct" if total and (correct / total) >= 0.7 else "Incorrect"
    
    return dominant, overall
