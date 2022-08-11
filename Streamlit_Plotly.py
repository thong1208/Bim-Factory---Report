import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from  plotly.subplots  import  make_subplots
import pyodbc 

#------------------------------------------------------------------------------------PHẦN TIÊU ĐỀ WEB-------------------------------------------------------------------------------------
st.set_page_config(page_icon= 'https://static.wixstatic.com/media/91d4d0_50c2e78106264db2a9ddda29a7ad0503~mv2.png/v1/fit/w_2500,h_1330,al_c/91d4d0_50c2e78106264db2a9ddda29a7ad0503~mv2.png',page_title='THE BIM FACTORY', layout='wide')
st.title('BIM Fee for Raffles MUR TD & SD')

#-------------------------------------------------------------------------------------PHẦN ĐỌC DATA----------------------------------------------------------------------------------------
df_time_sheet = pd.DataFrame(pd.read_csv("Logs-DB.csv"))
df_task = pd.DataFrame(pd.read_csv("tbTask.csv"))
df_project = pd.DataFrame(pd.read_csv("tbProject.csv"))

#--------------Connect SQL Server---------------
#conn_sqlServer = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
#                                'Server=192.168.67.252;'
#                                'Database=Polaris;'
#                                'UID=client;'
#                                'PWD=PolarisTBF2020;')
#sql_query1 = 'Select * From tbTimeSheet'
#sql_query2 = 'Select * From tbTask'
#sql_query3 = 'Select * From tbProject'
#df_time_sheet = pd.DataFrame(pd.read_sql(sql_query1, conn_sqlServer))
#df_task = pd.DataFrame(pd.read_sql(sql_query2, conn_sqlServer))
#df_project = pd.DataFrame(pd.read_sql(sql_query3, conn_sqlServer))

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
st.sidebar.header("Options filter")

df_time_task2 = df_time_task
project_name = df_time_task2['ProjectName'].unique().tolist()


project_selection = st.sidebar.multiselect("Project: ",
                                    project_name,
                                    default=project_name,
                                    )


project_role = df_time_task2['ProjectRule'].unique().tolist()
role_selection = st.sidebar.multiselect("Project Role: ",
                                project_role,
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
people = group['UserId'].max() #nunique(): tính sự khác biệt

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

config = dict({'staticPlot': True})
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
chart1.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.4,
            xanchor="left",
            x=0.01
            )
            )

#format ngày thành kiểu theo mong muốn
#group['TSDate'] = group['TSDate'].dt.strftime('%d - %b') 

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

maxHour = float(str(group['TSHour'].cumsum().max()))
maxUser = int(str(group['UserId'].max())) + 1
rangeHour = 0
for n in [10, 20, 50, 100, 200]:
        check = maxUser * n
        if check >= maxHour:
                rangeHour = check
                break
       
chart2 .update_layout(yaxis2 = dict(range = [0,rangeHour]),
                      yaxis1 = dict (range = [0,maxUser]),
                      xaxis = dict(type='date',
                                nticks=40,
                                tickformat="%d\n%b - %Y",
                                tickangle=0,)
                        )
chart2.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="left",
            x=0.05
            ))




#------------------------------------------------------------------------------HIỂN THỊ DATA LÊN STREAMLIT------------------------------------------------------------------------------
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

html_people =   f'''
                <div style="background-color: Black; padding: 5px">
                <h1 style= "color: White; text-align: center; font-size: 20px;">People: {people}</h1>
                </div>
                '''
                
html_hours =   f'''
                <div style="background-color: Black; padding: 5px; ">
                <h1 style= "color: White; text-align: center; font-size: 20px;">Total Hours: {total_hour}</h1>
                </div>
                '''
col1, col2 = st.columns(2)

with col1:
    st.markdown ( html_people, unsafe_allow_html=True )
    
with col2:
    st.markdown ( html_hours, unsafe_allow_html=True )

    
st.plotly_chart(chart1, config=config, use_container_width=True)                 
st.plotly_chart(chart2, config=config, use_container_width=True)

st.subheader('Details')
df_details = df_time_task2[['ProjectName', 'TaskType' , 'ProjectRule' , 'TSDate', 'TSHour']]
df_details = df_details.rename ({'ProjectRule': 'Project Role',
                                 'TSDate': 'TS Date',
                                 'TSHour': 'TS Hour',
                                 'TaskType' : 'Task Type',
                                 'ProjectName' : 'Project Name'}, axis=1)
#Ẩn cột chỉ mục 
blankIndex=[''] * len(df_details)
df_details.index=blankIndex

st.dataframe(df_details)
