
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from  plotly.subplots  import  make_subplots 

#------------------------------------------------------------------------------------PHẦN TIÊU ĐỀ WEB-------------------------------------------------------------------------------------
st.set_page_config(page_icon= 'https://static.wixstatic.com/media/91d4d0_50c2e78106264db2a9ddda29a7ad0503~mv2.png/v1/fit/w_2500,h_1330,al_c/91d4d0_50c2e78106264db2a9ddda29a7ad0503~mv2.png',page_title='Bim Factory - Report', layout='wide')
st.title('BIM Fee for Raffles MUR TD & SD')

#-------------------------------------------------------------------------------------PHẦN ĐỌC DATA----------------------------------------------------------------------------------------
df_time_sheet = pd.DataFrame(pd.read_csv("Logs-DB.csv"))
df_task = pd.DataFrame(pd.read_csv("tbTask.csv"))
df_project = pd.DataFrame(pd.read_csv("tbProject.csv"))

df_time_sheet = df_time_sheet[['ProjectId', 'TaskId', 'UserId', 'ProjectRule', 'TSDate', 'TSHour' ]]
df_task = df_task[['ProjectId', 'TaskId', 'TaskType']]
df_project = df_project[['ProjectId', 'ProjectName']]


#-------XÓA DỮ LIỆU NULL--------------------------------------------------------------------------------------
        #df_time_sheet = df_time_sheet.dropna( axis=1, how='all')
        #df_time_sheet = df_time_sheet.dropna( axis=0, how='all')

#------------------------------------------------------------------------------LẤY DATA TƯƠNG ỨNG VỚI YÊU CẦU------------------------------------------------------------------------------
df_time_sheet = df_time_sheet.loc[(df_time_sheet['ProjectId'] == 'PRO-121-LW-09') | (df_time_sheet['ProjectId'] == 'PRO-121-LW-10')]
df_task = df_task[(df_task['ProjectId'] == 'PRO-121-LW-09') | (df_task['ProjectId'] == 'PRO-121-LW-10')]
df_time_sheet['TSDate']= pd.to_datetime(df_time_sheet['TSDate'])

#-------------------------------------------------------------------------------------NỐI BẢNG 'jion()'------------------------------------------------------------------------------------
df_time_task = df_time_sheet.join(df_task.set_index(['ProjectId', 'TaskId']),
                                  on=(['ProjectId','TaskId']))
df_time_task = df_time_task.join(df_project.set_index(['ProjectId']),
                                 on= (['ProjectId']))


#------------------------------------------------------------------------------------Filter Dataframe--------------------------------------------------------------------------------------
df_time_task2 = df_time_task
project_name = df_time_task2['ProjectName'].unique().tolist()
project_selection = st.multiselect("Project: ",
                                    project_name,
                                    default=project_name,
                                    )

project_role = df_time_task2['ProjectRule'].unique().tolist()
project_role2 = project_role
role_selection = st.multiselect("Project Role: ",
                                project_role2,
                                default=project_role[0:2])


mask = (df_time_task2['ProjectName'].isin(project_selection) & df_time_task2['ProjectRule'].isin(role_selection))
#number = df_time_task2[mask].shape[0]
df_time_task2 = df_time_task2[mask]


group_tsHour = df_time_task2.groupby(['TaskType' , 'ProjectRule'], as_index=False)['TSHour'].sum()
group1 = df_time_task2.groupby(['TSDate'], as_index=False)['TSHour'].sum() 
group2 = df_time_task2.groupby(['TSDate'], as_index=False)['UserId'].nunique() 
group = group1.join(group2.set_index(['TSDate']), on=(['TSDate']))

#------Chuyển đổi thành các kiểu dữ liệu thích hợp tự động-----------------------------------------------
df_time_sheet = df_time_sheet.convert_dtypes()



#------TÍNH TOÁN CÁC SỐ---------------------------------
total_hour = df_time_task2['TSHour'].sum() 
#projects = df_time_task['ProjectId'].nunique() 
people = df_time_task2['UserId'].nunique() #nunique(): tính sự khác biệt


#-------------------
#chart_hours = px.histogram(df_time_task, x='TaskType', y='TSHour', color='ProjectRule', text_auto= True,
#                           labels={
#                                    "TaskType" : "Task Type",
#                                    "TSHour" : "Hours",
#                                    "ProjectRule" : "Role"
#                          })

#chart_people = px.histogram(df_time_task, x='TSDate' , y='UserId', text_auto= True, histfunc= 'count',nbins = 20,
#                            labels={
#                                    "TSDate" : "Date",
#                                    "UserId" : "Hours",
#                                    "ProjectRule" : "Role"
#                           }).update_layout(bargap=0.2)
#-------------------



#---------------------------------------------------------------------------------------------BIỂU DIỄN ĐỒ THỊ------------------------------------------------------------------------------
HEIGHT = 250
WIDTH = 400
chart1 = px.bar(group_tsHour,
                x='TSHour', y='TaskType' ,
                orientation='h',
                color='ProjectRule',
                text_auto=True,
                color_discrete_sequence=['#333333','#AAAAAA'],
                labels={
                        "TaskType" : "",
                        "TSHour" : "Hours",
                        "ProjectRule" : ""
                })

chart1_1 = px.bar(group_tsHour,
                x='TSHour', y='TaskType' ,
                orientation='h',
                color='ProjectRule',
                text_auto=True,
                height=HEIGHT,
                width= WIDTH,
                color_discrete_sequence=['#333333','#AAAAAA'],
                labels={
                        "TaskType" : "",
                        "TSHour" : "Hours",
                        "ProjectRule" : ""
                })

chart2   =  make_subplots ( specs = [[{ "secondary_y" :  True}]]) 
chart2 .add_trace(
        go.Bar(x=group['TSDate'], y=group['UserId'],
               name= 'Participants by date',
               marker_color = '#333333', 
               text=group['UserId']),
               secondary_y=False)

chart2 .add_trace(
        go.Scatter(x=group['TSDate'], y=group['TSHour'],
                   name= 'Man-hours per day',
                   mode = 'lines + markers+text',
                   textposition='top center',
                   textfont=dict(color='#FF6600', size = 10),
                   text=group['TSHour']),
                   secondary_y=True, )

chart2 .add_trace(
        go.Scatter(x=group['TSDate'], y=group['TSHour'].cumsum(),
                   name= 'Accumulated Man-hours',
                   mode = 'lines + markers + text',
                   textposition='top center',
                   textfont=dict(color='#00FFCC', size = 10),
                   text=group['TSHour'].cumsum()),
                   secondary_y=True, )

chart2 .update_layout(yaxis2 = dict(range = [0,1000]),
                      yaxis1 = dict (range = [0,14]),
                      )




#------------------------------------------------------------------------------HIỂN THỊ DATA LÊN STREAMLIT------------------------------------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    st.write('People',people)
    
with col2:
    st.write('Total Hours',total_hour)

#container = st.empty()
#button_A = container.button('Btn A')

#if button_A is True:
#        container.empty()
#        st.plotly_chart(chart1)
#        button_B = container.button('Btn B')
#else:
#        st.plotly_chart(chart1_1)
#myKey = 'my_key'
#if myKey not in st.session_state:
#        st.session_state[myKey] = False
#if st.session_state[myKey]:
#       myBtn = st.button('Button 1')
#        st.plotly_chart(chart1)
#        st.session_state[myKey] = False
#else:
#        myBtn = st.button('Button 2')
#        st.plotly_chart(chart1_1)
#        st.session_state[myKey] = True
col11, col22 = st.columns(2)
with col1:
    st.plotly_chart(chart1)    
    
with col2:
    st.plotly_chart(chart2)
st.plotly_chart(chart1)                 
st.plotly_chart(chart2)
st.subheader('Details')
st.dataframe(df_time_task2)
st.write('OKe')
