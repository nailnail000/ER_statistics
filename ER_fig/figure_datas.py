import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

from ER_datas.id_characterName import LoadCharacter
dic_characterNum_Name=LoadCharacter()

def plot_set_data(plt,data,condition):
    x_type=condition[0]
    y_type=condition[1]
    plt.plot(data[x_type], data[y_type],'o')
    plt.xlabel(x_type,labelpad=10)
    plt.ylabel(y_type,labelpad=10)
    # plt.plot(mmr_ranges,mmr_lines,'r')
    plt.subplots_adjust(left=0.07,bottom=0.06,top=0.9)

from ER_datas.rank_mmr import mmr_line
def plot_mmrcharge_set_data(plt,data,condition):
    x_type=condition[0]
    y_type=condition[1]
    plt.plot(data[x_type], data[y_type],'o')
    plt.xlabel(x_type,labelpad=10)
    plt.ylabel(y_type,labelpad=10)
    figure_red=mmr_line()
    plt.plot(figure_red[x_type],figure_red[y_type],'r')
    plt.subplots_adjust(left=0.07,bottom=0.06,top=0.9)

dic_figureType_setData={
"plot":plot_set_data,
"plot_mmrcharge":plot_mmrcharge_set_data
}

def figure_save(dic_datas,figure_type,condition):
    for i in dic_characterNum_Name:
        # 한글화
        i=int(i)
        datas=dic_datas.dic_characterNum_datas.get(i,{})
        if datas == {}:
            continue
        plt.rcParams["font.family"] = 'Malgun Gothic'
        plt.style.use('_mpl-gallery')
        mpl.rcParams['axes.unicode_minus'] = False
        #그래프 이름과 사이즈
        plt.figure(i,figsize=(10,6))
        plt.title(dic_characterNum_Name[str(i)],pad=10)
        plt.savefig("fig/"+dic_characterNum_Name[str(i)]+"mmr_mmrGain")
        
        #데이터 설정
        dic_figureType_setData[figure_type](plt,datas,condition)
        #그래프 보기
        plt.show()
        #figure삭제
        plt.cla()   # clear the current axes
        plt.clf()   # clear the current figure
        plt.close() # closes the current figure