'''
11. left_shoulder
12. right_shoulder
13. left_elbow
14. right_elbow
15. left_wrist
16. right_wrist
17. left_pinky
18. right_pinky
19. left_index (中指?)
20. right_index
21. left_thunb
22. right_thunb
23. left_hip (骨盆?)
24. right_hip
25. left_knee
26. right_knee
27. left_ankle
28. right_ankle
29. left_heel (腳跟)
30. right_heel
31. left_foot_index
32. right_foot_index (腳中指)
'''

NOSE = 0
LEFT_SHOULDER = 11
RIGHT_SHOULDER = 12
LEFT_ELBOW = 13
RIGHT_ELBOW = 14
LEFT_WRIST = 15
RIGHT_WRIST = 16
LEFT_HIP = 23
RIGHT_HIP = 24
LEFT_KNEE = 25
RIGHT_KNEE = 26
LEFT_ANKLE = 27
RIGHT_ANKLE = 28
RIGHT_FOOT = 32

WARRIOR_II_ANGLE = {
    "LEFT_SHOULDER": [LEFT_ELBOW, LEFT_SHOULDER, LEFT_HIP],
    "RIGHT_SHOULDER": [RIGHT_ELBOW, RIGHT_SHOULDER, RIGHT_HIP],
    "LEFT_ELBOW": [LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST],
    "RIGHT_ELBOW": [RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST],
    "LEFT_HIP": [RIGHT_HIP, LEFT_HIP, LEFT_KNEE],
    "RIGHT_HIP": [LEFT_HIP, RIGHT_HIP, RIGHT_KNEE],
    "LEFT_KNEE": [LEFT_HIP, LEFT_KNEE, LEFT_ANKLE],
    "RIGHT_KNEE": [RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE],
    "RIGHT_ANKLE": [RIGHT_KNEE, RIGHT_ANKLE, RIGHT_FOOT],
}