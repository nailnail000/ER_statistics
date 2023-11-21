#save api datas
#from ER_apis.ER_api import save_games
#save_games(27721413,27721414)



#doc string
dic_dataType_figureType={
    "data_type":{"figure_type":{"data_condition":[]}}
    ,

    "filter": {"!*":{"condition:datas"}},
    "data_cleansing":{
        "plot":{"condition":["*","*"]},
        "plot_mmrcharge":{"condition":["mmrBefore","mmrGain"]}},
    "mmrGain_option": {
        "plot":{"condition":["*"]},
        "plot_mmrcharge":{"condition":["mmrBefore"]}
    }
           }
#sort datas
import numpy as np
import matplotlib.pyplot as plt
from ER_datas.ERDataCleansing import ERDataCleansing
plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False
tier_range={}
tier_range[0]="아이언"
tier_range[1000]="브론즈"
tier_range[2000]="실버"
tier_range[3000]="골드"
tier_range[4000]="플레티넘"
tier_range[5000]="다이아"
tier_range[6000]="데미갓"
tier_range["all"]="all"
data_type="camera"
list_request_datatype=["addSurveillanceCamera","mmrgain","mmrBefore","gameRank"]
dic_characterNum_datas=ERDataCleansing(29889463,29889463,data_type,list_request_datatype)
add_camera1=dic_characterNum_datas.addSurveillanceCamera
add_camera2=dic_characterNum_datas.addTelephotoCamera
add_camera=[add_camera1[i]+add_camera2[i] for i in range(len(add_camera1))]
x_add_camera=set(add_camera)

#카메라 설치 수에 따른 mmr획득량
y_mmrGain_camera=[[] for i in range(len(x_add_camera))]
y_mmrGain=dic_characterNum_datas.mmrGain
y_mmrGain_group=[[add_camera[i],y_mmrGain[i]] for i in range(len(y_mmrGain))]
for i in range(len(y_mmrGain_group)):
    for j in range(len(x_add_camera)):
        if y_mmrGain_group[i][0]==j:
            y_mmrGain_camera[j].append(y_mmrGain_group[i][1])
y_mmrGain_average=[np.mean(i) for i in y_mmrGain_camera]

y_pos=np.arange(len(y_mmrGain_average))
plt.bar(y_pos,y_mmrGain_average, align='center', alpha=0.5)
plt.xticks(y_pos,x_add_camera)
plt.show

#티어별 카메라 설치 평균
y_mmrBefore=dic_characterNum_datas.mmrBefore
y_mmrBefore_thousand=[(y_mmrBefore[i]%10000//1000)*1000 for i in range(len(y_mmrBefore))]
for i in range(len(y_mmrBefore_thousand)):
    if y_mmrBefore_thousand[i]>6000:
        y_mmrBefore_thousand[i]=6000
y_mmrBefore_thousandset=list(set(y_mmrBefore_thousand))
y_mmrBefore_tier=[tier_range[y_mmrBefore_thousandset[i]] for i in range(len(y_mmrBefore_thousandset))]
y_mmrBefore_group=[[add_camera[i],y_mmrBefore_thousand[i]] for i in range(len(y_mmrBefore_thousand))]
y_mmrBefore_tier_camera=[[] for i in range(len(y_mmrBefore_tier))]
for i in range(len(y_mmrBefore_group)):
    for j in range(len(y_mmrBefore_tier)):
        if y_mmrBefore_group[i][1]==y_mmrBefore_thousandset[j]:
            y_mmrBefore_tier_camera[j].append(y_mmrBefore_group[i][0])
y_mmrBefore_average=[np.mean(i) for i in y_mmrBefore_tier_camera]

y_pos=np.arange(len(y_mmrBefore_average))
plt.bar(y_pos,y_mmrBefore_average, align='center', alpha=0.5)
plt.xticks(y_pos,y_mmrBefore_tier)
plt.show

#1등했을 때 평균 카메라 설치 수
y_gameRank=dic_characterNum_datas.gameRank
y_gameRank_group=[[add_camera[i],y_gameRank[i]] for i in range(len(y_gameRank))]
y_gameRank_win_camera=[y_gameRank_group[i][0] for i in range(len(y_gameRank_group)) if y_gameRank_group[i][1] == 1]
y_gameRank_win_average=np.mean(y_gameRank_win_camera)
print(y_gameRank_win_average)

#순방했을 때 평균 카메라 설치 수
y_gameRank=dic_characterNum_datas.gameRank
y_gameRank_group=[[add_camera[i],y_gameRank[i]] for i in range(len(y_gameRank))]
y_gameRank_camera=[y_gameRank_group[i][0] for i in range(len(y_gameRank_group)) if y_gameRank_group[i][1] < 3]
y_gameRank_average=np.mean(y_gameRank_camera)
print(y_gameRank_average)


#figure 
# from ER_fig.figure_datas import figure_save
# figure_type="plot_mmrcharge"
# list_request_datatype=["mmrBefore","mmrGain"]
# figure_save(dic_characterNum_datas,figure_type,list_request_datatype)


