import mediapipe as mp
import cv2
import json
import math as m
import AngleNodeDef

mp_pose = mp.solutions.pose
pose_connection = mp_pose.POSE_CONNECTIONS
nodeList = mp.solutions.pose.PoseLandmark
mp_sample_pose = mp_pose.Pose(static_image_mode=True,
                                        model_complexity=2,
                                        min_detection_confidence=0.5)
mp_result_pose = mp_pose.Pose(static_image_mode=False,
                                        model_complexity=2,
                                        min_detection_confidence=0.5)

def getMediapipeResult(frame, mode=True):
    try:
        if mode:
            results = mp_sample_pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        else:
            results = mp_result_pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        point2d = results.pose_landmarks.landmark
        point3d = results.pose_world_landmarks.landmark
        return point2d, point3d
    except:
        return 0, 0

def getLandmarks(landmark, w=None, h=None):
    '''
    Get landmark x,y,z respectively
    '''
    if w == None or h == None:
        return landmark.x, landmark.y, landmark.z
    else:
        return int(landmark.x*w), int(landmark.y*h)

def readSampleJsonFile(path):
    try:
        with open(path, 'r') as file:
            sample_angle = json.load(file)
            return sample_angle
    except:
        return None

def writeSampleJsonFile(angle_array, angle_def, path):
    data = {}
    index = 0
    for key,_ in angle_def.items():
        data[key] = angle_array[index]
        index+=1
    print(data)
    with open(path, 'w') as file:
        json.dump(data, file)

def computeAngle(point1, centerPoint, point2):
    p1_x, pc_x, p2_x = point1[0], centerPoint[0], point2[0]
    p1_y, pc_y, p2_y = point1[1], centerPoint[1], point2[1] 

    if len(point1) == len(centerPoint) == len(point2) == 3:
        # 3 dim
        p1_z, pc_z, p2_z = point1[2], centerPoint[2], point2[2]
    else:
        # 2 dim
        p1_z, pc_z, p2_z = 0,0,0

    # vector
    x1,y1,z1 = (p1_x-pc_x),(p1_y-pc_y),(p1_z-pc_z)
    x2,y2,z2 = (p2_x-pc_x),(p2_y-pc_y),(p2_z-pc_z)

    # angle
    cos_b = (x1*x2 + y1*y2 + z1*z2) / (m.sqrt(x1**2 + y1**2 + z1**2) *(m.sqrt(x2**2 + y2**2 + z2**2)))
    B = m.degrees(m.acos(cos_b))
    return B

def treePoseRule(roi, tips, sample_angle_dict, angle_dict, point3d):
    for key, value in roi.items():
        tip_flag = False
        if tips == "":
            tip_flag = True
        if key == 'LEFT_KNEE' or key == 'LEFT_HIP':
            tolerance_val = 8
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            if angle_dict[key]>=min_angle and angle_dict[key]<=max_angle:
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認左腳重心，避免左腳傾斜造成負擔"
        elif key == 'RIGHT_FOOT_INDEX':
            _,foot_y,_ = getLandmarks(point3d[AngleNodeDef.RIGHT_FOOT_INDEX])
            _,knee_y,_ = getLandmarks(point3d[AngleNodeDef.LEFT_KNEE])
            if foot_y <= knee_y:
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認右腳腳尖須高於左腳膝蓋，避免造成膝蓋負擔"
        elif key == 'RIGHT_KNEE':
            _,_,knee_z = getLandmarks(point3d[AngleNodeDef.RIGHT_KNEE])
            _,_,hip_z = getLandmarks(point3d[AngleNodeDef.RIGHT_HIP])
            if angle_dict[key]<=60 and ((hip_z-knee_z)*100)<=15:
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認右腳膝蓋不可往前傾，須與髖關節保持同一平面"
        elif key == 'RIGHT_HIP':
            if angle_dict[key]>=100:
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認右腳膝蓋是否正確抬起"
        elif key == 'LEFT_SHOULDER' or key == 'RIGHT_SHOULDER':
            if angle_dict[key]>=120:
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認雙手是否高舉在頭部之上"
        elif key == 'LEFT_ELBOW' or key == 'RIGHT_ELBOW':
            if angle_dict[key]>=90:
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認手軸是否盡量往上伸直"
        elif key == 'LEFT_INDEX' or key == 'RIGHT_INDEX':
            index_x,_,_ = getLandmarks(point3d[AngleNodeDef.LEFT_INDEX]) if key == 'LEFT_INDEX' else getLandmarks(point3d[AngleNodeDef.RIGHT_INDEX])
            left_shoulder_x,_,_ = getLandmarks(point3d[AngleNodeDef.LEFT_SHOULDER])
            right_shoulder_x,_,_ = getLandmarks(point3d[AngleNodeDef.RIGHT_SHOULDER])
            if index_x>=right_shoulder_x and index_x<=left_shoulder_x:
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認雙手合掌並往上伸直於兩側肩膀中間"
    if tips == "":
        tips = "動作正確 ! "
    return roi, tips

def WarriorIIPoseRule(roi, tips, sample_angle_dict, angle_dict, point3d):
    for key, value in roi.items():
        tip_flag = False
        if tips == "":
            tip_flag = True
        if key == 'RIGHT_ANKLE':
            tolerance_val = 5
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            if angle_dict[key]>=min_angle and angle_dict[key]<=max_angle:
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認右腳腳尖須朝向墊子右方"
        elif key == 'RIGHT_KNEE':
            ankle_x,_,_ = getLandmarks(point3d[AngleNodeDef.RIGHT_ANKLE])
            knee_x,_,_ = getLandmarks(point3d[AngleNodeDef.RIGHT_KNEE])
            if angle_dict[key]>=90 and angle_dict[key]<=150 and abs((ankle_x-knee_x)*100)<=10:
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認右腳膝蓋與腳踝的關節點須重疊，\n並注意大腿下壓的角度"
        elif key == 'LEFT_KNEE':
            tolerance_val = 10
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            if angle_dict[key]>=min_angle and angle_dict[key]<=max_angle:
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認左腳需盡量伸直，且左腳腳尖需朝向墊子前方"
        elif key == 'LEFT_HIP' or key == 'RIGHT_HIP':
            if angle_dict[key]>=100:
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認兩側骨盆向外打開並挺胸"
        elif key == 'NOSE':
            nose_x,_,_ = getLandmarks(point3d[AngleNodeDef.NOSE])
            left_hip_x,_,_ = getLandmarks(point3d[AngleNodeDef.LEFT_HIP])
            right_hip_x,_,_ = getLandmarks(point3d[AngleNodeDef.RIGHT_HIP])
            if nose_x>=(right_hip_x-0.1) and nose_x<=(left_hip_x+0.1):
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認頭部位於骨盆正上方，且將頭轉向彎曲腳的方向"
        elif key == 'LEFT_SHOULDER' or key == 'RIGHT_SHOULDER':
            tolerance_val = 5
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            if angle_dict[key]>=min_angle and angle_dict[key]<=max_angle:
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認兩側肩膀不要過度用力，並將背部挺直，\n盡量將身體面向正面"
        elif key == 'LEFT_ELBOW' or key == 'RIGHT_ELBOW':
            tolerance_val = 5
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            if angle_dict[key]>=140 and (angle_dict[key]>=min_angle and angle_dict[key]<=max_angle):
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認雙手是否平舉並伸向墊子兩側"
    if tips == "":
        tips = "動作正確 ! "
    return roi, tips

def ReversePlankPoseRule(roi, tips, sample_angle_dict, angle_dict, point3d):
    for key, value in roi.items():
        tip_flag = False
        if tips == "":
            tip_flag = True
        if key == 'NOSE':
            node_x,_,_ = getLandmarks(point3d[AngleNodeDef.NOSE])
            left_hip_x,_,_ = getLandmarks(point3d[AngleNodeDef.LEFT_HIP])
            right_hip_x,_,_ = getLandmarks(point3d[AngleNodeDef.RIGHT_HIP])
            if node_x>left_hip_x and node_x>right_hip_x:
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認頭部需朝向左邊"
        elif key == 'LEFT_ELBOW':
            tolerance_val = 10
            min_angle = sample_angle_dict[key]-tolerance_val
            # max_angle = sample_angle_dict[key]+tolerance_val
            if angle_dict[key]>=min_angle:
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認雙手手軸是否與肩膀成一條線"
        elif key == 'LEFT_WRIST':
            tolerance_val = 10
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            if angle_dict[key]>=min_angle and angle_dict[key]<=max_angle:
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認雙手手腕是否與手軸成一條線"
        elif key == 'LEFT_INDEX':
            index_x,_,_ = getLandmarks(point3d[AngleNodeDef.LEFT_INDEX])
            wrist_x,_,_ = getLandmarks(point3d[AngleNodeDef.LEFT_WRIST])
            if index_x < wrist_x:
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認手指需朝向臂部方向"
        elif key == 'LEFT_SHOULDER':
            tolerance_val = 10
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            if angle_dict[key]>=min_angle and angle_dict[key]<=max_angle:
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認手臂需與地面盡量垂直"
        elif key == 'LEFT_HIP':
            tolerance_val = 5
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            if angle_dict[key]>=min_angle:
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認臂部是否有抬起，並與脊椎呈一條線"
        elif key == 'LEFT_KNEE':
            tolerance_val = 5
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            if angle_dict[key]>=min_angle:
                roi[key] = True
            else:
                roi[key] = False
                if tip_flag == True:
                    tips = "請確認雙腳需與上半身呈一條線"
    if tips == "":
        tips = "動作正確 ! "
    return roi, tips