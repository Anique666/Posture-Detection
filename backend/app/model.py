import mediapipe as mp
import cv2 as cv
import math as m

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5)

def calculate_angle(p1, p2, p3):
    v1 = (p1.x - p2.x, p1.y - p2.y)
    v2 = (p3.x - p2.x, p3.y - p2.y)
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
    magnitude_v1 = m.sqrt(v1[0] ** 2 + v1[1] ** 2)
    magnitude_v2 = m.sqrt(v2[0] ** 2 + v2[1] ** 2)
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        return 0
    cos_theta = dot_product / (magnitude_v1 * magnitude_v2)
    cos_theta = max(-1.0, min(1.0, cos_theta))
    angle = m.acos(cos_theta)
    return m.degrees(angle)

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

    if a_k_a > 170 and avg_s_y < avg_h_y < avg_k_y:
        return "Standing"
    elif avg_s_y < avg_h_y < avg_k_y and a_k_a < 150:
        return "Squatting"
    elif avg_s_y < avg_h_y < avg_k_y and a_k_a >= 150:
        return "Sitting"
    else:
        return "Other"

def calculate_torso_angle(landmarks):
    try:
        ls = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        rs = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        lh = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        rh = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    except IndexError:
        return None
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
    angle = m.degrees(m.acos(cos_theta))
    return 180 - angle

def check_squatting_posture(landmarks):
    try:
        rk = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
        ra = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
        lk = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
        la = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    except IndexError:
        return "Insufficient landmarks for squat check"

    back_angle = calculate_torso_angle(landmarks)
    right_knee_beyond_toe = rk.x > ra.x if rk and ra else False
    left_knee_beyond_toe = lk.x > la.x if lk and la else False

    reasons = []
    if right_knee_beyond_toe or left_knee_beyond_toe:
        reasons.append("Knee(s) beyond toe")
    if back_angle is not None and back_angle < 140:
        reasons.append(f"Back angle too small: {back_angle:.1f}°")
    if reasons:
        return "Incorrect Squatting Posture: " + ", ".join(reasons)
    return "Correct Squatting Posture"

def check_sitting_posture(landmarks):
    try:
        rs = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        rh = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
        re = landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value]
        ls = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        lh = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        le = landmarks[mp_pose.PoseLandmark.LEFT_EAR.value]
    except IndexError:
        return "Insufficient landmarks for sitting check"

    right_neck_angle = calculate_angle(rs, rh, re) if rs and rh and re else None
    left_neck_angle = calculate_angle(ls, lh, le) if ls and lh and le else None
    if right_neck_angle is not None and left_neck_angle is not None:
        neck_angle = (right_neck_angle + left_neck_angle) / 2
    elif right_neck_angle is not None:
        neck_angle = right_neck_angle
    elif left_neck_angle is not None:
        neck_angle = left_neck_angle
    else:
        neck_angle = None

    back_angle = calculate_torso_angle(landmarks)

    reasons = []
    if neck_angle is not None and neck_angle > 30:
        reasons.append(f"Neck bent: {neck_angle:.1f}°")
    if back_angle is not None and abs(back_angle - 180) > 30:
        reasons.append(f"Back not straight: {back_angle:.1f}°")
    if reasons:
        return "Incorrect Sitting Posture: " + ", ".join(reasons)
    return "Correct Sitting Posture"

def run_pose_model(file_path: str) -> dict:
    cap = cv.VideoCapture(file_path)
    total_sit = total_squat = 0
    bad_sit = bad_squat = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        result = pose.process(rgb_frame)

        if result.pose_landmarks:
            landmarks = result.pose_landmarks.landmark
            pose_type = classify_posture(landmarks)

            if pose_type == "Squatting":
                total_squat += 1
                feedback = check_squatting_posture(landmarks)
                if "Incorrect" in feedback:
                    bad_squat += 1

            elif pose_type == "Sitting":
                total_sit += 1
                feedback = check_sitting_posture(landmarks)
                if "Incorrect" in feedback:
                    bad_sit += 1

    cap.release()


    summary = {}
    if total_sit == 0 and total_squat == 0:
        summary["feedback"] = "No sitting or squatting posture detected"
    elif total_sit >= total_squat:
        
        if total_sit > 0:
            summary["posture"] = "Sitting"
            summary["feedback"] = (
                "Incorrect Sitting Posture"
                if bad_sit / total_sit > 0.5
                else "Correct Sitting Posture"
            )
    else:
        
        if total_squat > 0:
            summary["posture"] = "Squatting"
            summary["feedback"] = (
                "Incorrect Squatting Posture"
                if bad_squat / total_squat > 0.5
                else "Correct Squatting Posture"
            )

    return summary
