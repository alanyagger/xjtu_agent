<template>
    <header class="page-layout-header">
      <div class="page-layout-row">
        <HeaderView />
      </div>
    </header>
  <div class="pandle-box">
    <div class="pandle-box-right">
      <div class="pandle-box-right-serach">
        <div class="calendar-header-box">
          <div class="search-container">
            <a-input-search
              v-model:value="searchValue"
              placeholder="请输入日程关键词"
              style="width: 180px"
              @search="handleSearch"
              @change="handleInputChange"
            />
            <!-- 搜索结果下拉框 -->
            <div 
              class="search-dropdown" 
              v-if="showSearchResult && filteredSchedules.length"
            >
              <ul>
                <li 
                  v-for="schedule in filteredSchedules" 
                  :key="schedule.id"
                  @click="handleScheduleClick(schedule)"
                  :style="{borderLeft: `3px solid ${schedule.backgroundColor}`}"
                >
                  <div class="schedule-title">{{ schedule.title }}</div>
                  <div class="schedule-time">{{ schedule.extendedProps.start }} - {{ schedule.extendedProps.end_time }}</div>
                </li>
              </ul>
            </div>
          </div>
        </div>   
        <div class="calendar-header-box calendar-header">
          <left-outlined @click="handleChangeTime('prive')" />
          <span class="calendar-header-time">{{currentTimeShow}}</span>
          <right-outlined @click="handleChangeTime('next')"/>
        </div>
        <div class="calendar-header-box" style="display: flex">
          <a-button type="primary" class='btn-mg' @click="addSchedule"><plus-outlined />新建日程</a-button>
          <a-radio-group v-model:value="currentType" class='btn-mg' @change="toggleCurrentType">
            <a-radio-button value="month">月</a-radio-button>
            <a-radio-button value="week">周</a-radio-button>
            <a-radio-button value="day">日</a-radio-button>
          </a-radio-group>
          <a-button class='btn-mg' @click="setCurrentTime">今天</a-button>
        </div>
      </div>
      <div class="CalendarBox" ref="CalendarBox">
        <FullCalendar :options="calendarOptions" ref="calendarRef" class="eventDeal-wrap" id="calendarRef">
          <template v-slot:eventContent="arg">
            <a-popover :overlayClassName="currentType === 'month' ? 'month-popover' : ''"
              :overlayStyle="{ zIndex: 9999 }">
              <template #content>
                <p>名称：{{arg.event.title}}</p>
                <p>时间：{{arg.event.extendedProps.start}} - {{arg.event.extendedProps.end_time}}</p>
                <p v-if="arg.event.extendedProps.remark">描述：{{arg.event.extendedProps.remark}}</p>
                <div class="event-actions">
                  <a-button 
                    type="link" 
                    danger 
                    size="small" 
                    @click.stop="handleDeleteEvent(arg.event.id)"
                  >
                    删除
                  </a-button>
                </div>
              </template>
              <div class="CalendarItem" 
                  :style="[{'background': arg.event.backgroundColor}, 
                          {'padding': '2px 4px'}, 
                          {'border-radius': '3px'},
                          {'margin': '1px'},
                          {'color': arg.event.textColor}]">
                
                <!-- 月视图：标题和时间同一行 -->
                <div v-if="currentType === 'month'" class="month-event-content">
                  <span class="fc-event-title fc-sticky" style="font-weight: bold;">
                    {{ arg.event.title }}
                  </span>
                  <span class="fc-event-time" style="font-size: 10px; margin-left: 4px;">
                    {{ arg.event.extendedProps.displayTime }}
                  </span>
                </div>
                
                <!-- 非月视图：保持原有布局（标题在上，时间在下） -->
                <div v-else>
                  <div class="fc-event-title fc-sticky" style="font-weight: bold;">
                    {{ arg.event.title }}
                  </div>
                  <div class="fc-event-time" style="font-size: 10px;">
                    {{ arg.event.extendedProps.displayTime }}
                  </div>
                </div>
              </div>
            </a-popover>
          </template>
        </FullCalendar>
      </div>
      <!-- 新建日程弹窗 -->
      <a-modal
        v-model:visible="addModalVisible"
        title="新建日程"
        @ok="handleAddSchedule"
        @cancel="addModalVisible = false"
      >
        <a-form :model="newSchedule">
          <a-form-item label="标题">
            <a-input v-model:value="newSchedule.title" placeholder="请输入日程标题" />
          </a-form-item>
          
          <a-form-item label="开始时间">
            <a-date-picker
              v-model:value="newSchedule.start"
              show-time
              format="YYYY-MM-DD HH:mm"
              placeholder="选择开始时间"
              @change="handleStartTimeChange"
            />
          </a-form-item>

          <a-form-item label="结束时间">
            <a-date-picker
              v-model:value="newSchedule.end"
              show-time
              format="YYYY-MM-DD HH:mm"
              placeholder="选择结束时间"
            />
          </a-form-item>
          
          <a-form-item label="描述">
            <a-textarea v-model="newSchedule.description" rows=4 placeholder="输入日程描述（可选）" />
          </a-form-item>
          
          <a-form-item label="颜色">
            <a-radio-group v-model:value="newSchedule.color">
              <a-radio-button value="#2097f3"><span :style="{background: '#2097f3', display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', marginRight: '4px'}"></span>蓝色</a-radio-button>
              <a-radio-button value="#52c41a"><span :style="{background: '#52c41a', display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', marginRight: '4px'}"></span>绿色</a-radio-button>
              <a-radio-button value="#faad14"><span :style="{background: '#faad14', display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', marginRight: '4px'}"></span>黄色</a-radio-button>
              <a-radio-button value="#f5222d"><span :style="{background: '#f5222d', display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', marginRight: '4px'}"></span>红色</a-radio-button>
              <a-radio-button value="#722ed1"><span :style="{background: '#722ed1', display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', marginRight: '4px'}"></span>紫色</a-radio-button>
              <a-radio-button value="#eb2f96"><span :style="{background: '#eb2f96', display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', marginRight: '4px'}"></span>粉色</a-radio-button>
              <a-radio-button value="#fa8c16"><span :style="{background: '#fa8c16', display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', marginRight: '4px'}"></span>橙色</a-radio-button>
            </a-radio-group>
          </a-form-item>
        </a-form>
      </a-modal>
      <!-- 添加删除确认弹窗 -->
      <a-modal
        v-model:visible="deleteConfirmVisible"
        title="确认删除"
        @ok="confirmDelete"
        @cancel="deleteConfirmVisible = false"
      >
        <p>确定要删除这个日程吗？此操作不可撤销。</p>
      </a-modal>
    </div>
  </div>
</template>

<script>
import HeaderView from "@/components/CHeaderView.vue";
import FullCalendar from "@fullcalendar/vue3";
import dayGridPlugin from '@fullcalendar/daygrid'//日历格子显示
import interactionPlugin from "@fullcalendar/interaction";//交互
import timeGridPlugin from "@fullcalendar/timegrid";//日历时间轴显示
import zhLocale from "@fullcalendar/core/locales/zh-cn";//中文
import dayjs from 'dayjs';
import { LeftOutlined, RightOutlined, PlusOutlined } from '@ant-design/icons-vue';
export default {
  name: 'HelloWorld',
  components: {
    FullCalendar,
    LeftOutlined,
    RightOutlined,
    PlusOutlined,
    HeaderView
  },
  props: {
  },
  data(){
    return {
      dayjs,
      searchValue:'',
      filteredSchedules: [], // 过滤后的日程
      showSearchResult: false, // 是否显示搜索结果
      searchTimer: null, // 防抖计时器
      currentType:'month',//默认月份面板
      currentDefaultType:'month',//默认月份面板
      currentTime:dayjs(),//默认当前时间
      calendarApi:null,
      currentTimeShow:null,
      deleteConfirmVisible: false, // 控制删除确认弹窗显示
      eventToDelete: null, // 存储待删除的日程ID
      calendarOptions: {//日历配置
        plugins: [dayGridPlugin, timeGridPlugin,interactionPlugin ],
        initialView: 'dayGridMonth',
        headerToolbar:false,
        firstDay: '1', // 设置一周中显示的第一天是周几，周日是0，周一是1，以此类推
        locales: [zhLocale],
        handleWindowResize: true,
        locale: "zh-cn",
        weekNumberCalculation: 'ISO', // 与firstDay配套使用
        eventColor: '#3d8eec', // 全部日历日程背景色
        timeGridEventMinHeight: '20', // 设置事件的最小高度
        aspectRatio: '2', // 设置日历单元格宽高比
        height:'100%',
        fixedWeekCount:false,
        events: [], // 日程数组
        eventTimeFormat: { // 时间格式
          hour: '2-digit',
          minute: '2-digit',
          meridiem: false,
          hour12: false
        },
        editable: false, // 是否可以进行（拖动、缩放）修改
        selectable: true, // 是否可以选中日历格
        selectMirror: true,
        selectMinDistance: 0, // 选中日历格的最小距离
        dayMaxEventRows: 4, // for all non-TimeGrid views
        moreLinkContent: this.moreLinkContent, //当一块区域内容太多以"+2 more"格式显示时，这个more的名称自定义
        weekends: true,
        navLinks: false, // “xx周”是否可以被点击，默认false，如果为true则周视图“周几”被点击之后进入日视图
        selectHelper: false,
        selectEventOverlap: false, // 相同时间段的多个日程视觉上是否允许重叠，默认为true，允许
        nowIndicator: true, //周/日视图中显示今天当前时间点（以红线标记），默认false不显示
        select: this.handleDateClick, //选中日历格事件
        eventsSet: this.handleEvents, // 事件点击
        eventClick: this.handleEventClick, // 日程点击信息展示
        eventResize: this.onEventResize, // 事件时间区间调整
      },
      addModalVisible: false, // 控制弹窗显示状态
      newSchedule: {
        title: '',
        start: dayjs(),
        end: dayjs().add(1, 'hour'),
        description: '',
        color: '#2097f3',
      },
    }
  },
  mounted(){
    // 获取用户信息
    this.calendarApi = this.$refs.calendarRef.getApi();
    this.currentTimeShow = dayjs(this.currentTime).format('YYYY 年 MM 月')
    document.querySelector('.eventDeal-wrap')?.classList.add('month-view');
    document.addEventListener('click', (e) => {
      const searchContainer = document.querySelector('.search-container');
      if (searchContainer && !searchContainer.contains(e.target)) {
        this.showSearchResult = false;
      }
    });
  },
  async created() {
    this.spinningBoxRight = true
    this.getScheduleList()

  },
  methods:{
    // 获取日程列表
    async getScheduleList() {
      // let scheduleList =[{
      //   id: 211,
      //   calendar_id: 45,
      //   color: "",
      //   end_time: "2025-03-24T08:30:00",
      //   instructions: "",
      //   name: "测试",
      //   schedule_calendar: {color: "#aa47bc", name: "测试日历"},
      //   source: "default",
      //   start_time: "2025-03-24T08:00:00",
      // },{
      //   id: 212,
      //   calendar_id: 45,
      //   color: "",
      //   end_time: "2025-03-25T23:59:00",
      //   instructions: "",
      //   name: "跨天测试",
      //   schedule_calendar: {color: "#aa47bc", name: "测试日历"},
      //   source: "default",
      //   start_time: "2025-03-20T00:00:00",
      // }]
      let scheduleList=[]
      this.calendarOptions.events = scheduleList && scheduleList.length ? scheduleList.map((item) => {
        // 判断是否跨天
        const isCrossDay = this.isCrossDay(item.start_time, item.end_time);
        // 格式化显示时间
        let displayTime = '';
        if (isCrossDay) {
          displayTime = `${dayjs(item.start_time).format('MM-DD HH:mm')} - ${dayjs(item.end_time).format('MM-DD HH:mm')}`;
        } else {
          displayTime = `${dayjs(item.start_time).format('HH:mm')} - ${dayjs(item.end_time).format('HH:mm')}`;
        }
        
        return {
          id: item.id,
          title: item.name,
          start: dayjs(item.start_time).format('YYYY-MM-DDTHH:mm:00'),
          end: dayjs(item.end_time).format('YYYY-MM-DDTHH:mm:00'),
          backgroundColor: item.color ? item.color : '#2097f3',
          borderColor: item.color ? item.color : '#2097f3',
          textColor: '#fff', // 文字颜色设为白色
          className: (dayjs(item.end_time)).isBefore(dayjs()) ? "text-normal-gary" : "text-normal",
          extendedProps: {
            start: dayjs(item.start_time).format('YYYY-MM-DD HH:mm'),
            end_time: dayjs(item.end_time).format('YYYY-MM-DD HH:mm'),
            remark: item.remark,
            schcolor: item.color || '',
            calendarColor: item.schedule_calendar?.color || '',
            displayTime: displayTime
          },
          deleteConfirmVisible: false, // 删除确认弹窗显示状态
          eventToDelete: null, // 存储待删除的日程ID
        }
      }):[]
      
      setTimeout(() => {
        this.autoScaleFullCalendar();
      },1000)
    },
    // 新增日程
    addSchedule() {
      // 打开新建日程弹窗
      this.addModalVisible = true;
      
      // 重置新建日程表单数据
      this.newSchedule = {
        title: '',
        start: dayjs(),
        end: dayjs().add(1, 'hour'),
        description: '',
        color: '#2097f3',
      };
    },
    handleStartTimeChange(startTime) {
      if (!startTime) return;
      // 确保结束时间不早于开始时间
      if (this.newSchedule.end.isBefore(startTime)) {
        this.newSchedule.end = dayjs(startTime).add(1, 'hour');
      }
    },

    // 处理新建日程提交
    handleAddSchedule() {
      if (!this.newSchedule.title.trim()) {
        this.$message.error('请输入日程标题');
        return;
      }
      
      // 验证时间
      if (this.newSchedule.end.isBefore(this.newSchedule.start)) {
        this.$message.error('结束时间不能早于开始时间');
        return;
      }
      
      const loadingInstance = this.$message.loading('正在创建日程...', 0);
      
      setTimeout(() => {
        try {
          // 判断是否跨天
          const isCrossDay = this.isCrossDay(
            this.newSchedule.start.format('YYYY-MM-DDTHH:mm:00'),
            this.newSchedule.end.format('YYYY-MM-DDTHH:mm:00')
          );
          
          // 格式化显示时间
          let displayTime = '';
          if (isCrossDay) {
            displayTime = `${this.newSchedule.start.format('MM-DD HH:mm')} - ${this.newSchedule.end.format('MM-DD HH:mm')}`;
          } else {
            displayTime = `${this.newSchedule.start.format('HH:mm')} - ${this.newSchedule.end.format('HH:mm')}`;
          }
          
          // 构造新日程
          const newEvent = {
            id: Date.now(),
            title: this.newSchedule.title,
            start: this.newSchedule.start.format('YYYY-MM-DDTHH:mm:00'),
            end: this.newSchedule.end.format('YYYY-MM-DDTHH:mm:00'),
            
            backgroundColor: this.newSchedule.color,
            borderColor: this.newSchedule.color,
            textColor: '#fff',
            className: 'text-normal',
            eventDisplay: 'auto', 
            extendedProps: {
              start: this.newSchedule.start.format('YYYY-MM-DD HH:mm'),
              end_time: this.newSchedule.end.format('YYYY-MM-DD HH:mm'),
              remark: this.newSchedule.description,
              color: this.newSchedule.color,
              displayTime: displayTime
            },
          };
          
          console.log('新日程数据:', newEvent);
          
          this.calendarOptions.events.push(newEvent);
          this.addModalVisible = false;
          
          loadingInstance();
          this.$message.success('日程创建成功！');
          this.calendarApi.render();
        } catch (error) {
          loadingInstance();
          this.$message.error('创建日程失败：' + error.message);
          console.error('创建日程出错:', error);
        }
      }, 1000);
    },
    
    // 判断是否跨天
    isCrossDay(startTime, endTime) {
      return dayjs(startTime).format('YYYY-MM-DD') !== dayjs(endTime).format('YYYY-MM-DD');
    },
    // 处理删除事件（显示确认弹窗）
    handleDeleteEvent(eventId) {
      this.eventToDelete = eventId; // 记录要删除的日程ID
      this.deleteConfirmVisible = true; // 显示确认弹窗
    },
  
    // 确认删除
    confirmDelete() {
      if (this.eventToDelete) {
        // 从日程数组中过滤掉要删除的日程
        this.calendarOptions.events = this.calendarOptions.events.filter(
          event => event.id.toString() !== this.eventToDelete.toString()
        );
        // 重新渲染日历
        this.calendarApi.render();
        // 提示删除成功
        this.$message.success('日程已成功删除');
      }
      // 关闭弹窗并重置变量
      this.deleteConfirmVisible = false;
      this.eventToDelete = null;
    },
    // 点击日程事件-查看对应日程
    handleEventClick(clickInfo){
      console.log(clickInfo,'event')
    },
    
    // 返回至当前日期
    setCurrentTime(){
      this.currentTime = dayjs()
      this.calendarApi.today();
      // 根据 currentType 重新计算并更新 currentTimeShow
      if (this.currentType === 'day') {
        this.currentTimeShow = dayjs(this.currentTime).format('YYYY年MM月DD日');
      } else if (this.currentType === 'week') {
        this.currentTimeShow = this.calendarApi.view.title; 
      } else {
        this.currentTimeShow = dayjs(this.currentTime).format('YYYY 年 MM 月');
      }
    },
    
    // 日程视图-切换
    toggleCurrentType(){
      const calendarWrap = document.querySelector('.eventDeal-wrap');
      if(this.currentType == 'week'){
        this.$nextTick(function(){
          this.calendarApi = this.$refs.calendarRef.getApi();
          this.calendarApi.gotoDate(dayjs(this.currentTime).format('YYYY-MM-DD HH:mm'))
          this.changePanelShow('timeGridWeek')
          calendarWrap?.classList.remove('month-view');
        })
      }else if(this.currentType == 'month'){
        this.$nextTick(() => {
        this.calendarApi = this.$refs.calendarRef.getApi();
        this.calendarApi.gotoDate(dayjs(this.currentTime).format('YYYY-MM-DD HH:mm'));
        this.changePanelShow('dayGridMonth');
        // 添加月视图专属类名
        calendarWrap?.classList.add('month-view');
        })
      }else{
        this.$nextTick(() => {
        this.calendarApi = this.$refs.calendarRef.getApi();
        this.calendarApi.gotoDate(dayjs(this.currentTime).format('YYYY-MM-DD HH:mm'));
        this.changePanelShow('timeGridDay');
        this.currentTimeShow = dayjs(this.currentTime).format('YYYY年MM月DD日');
        calendarWrap?.classList.remove('month-view');
      });
      }
    },
    
    changePanelShow(type){
      this.calendarApi.changeView(type)
    },
    
    handleChangeTime(type){
      let changeTime = null
      if(type == 'prive'){
        changeTime = dayjs(this.currentTime).subtract(1,this.currentType)
      }else{
        changeTime = dayjs(this.currentTime).add(1,this.currentType)
      }
      this.currentTime = changeTime
      this.currentTimeShow = this.currentType == 'day' ? dayjs(this.currentTime).format('YYYY年MM月DD日'):(this.currentType == 'week' ?
        this.calendarApi.view.title:
        dayjs(this.currentTime).format('YYYY 年 MM 月'))
      this.calendarApi.gotoDate(dayjs(changeTime).format('YYYY-MM-DD HH:mm'))
    },
    
    // 增加自适应大小调整的特性
    autoScaleFullCalendar() {
      document.getElementsByClassName('fc-col-header') && document.getElementsByClassName('fc-col-header')[0].removeAttribute('style');
      document.getElementsByClassName('fc-daygrid-body') && document.getElementsByClassName('fc-daygrid-body')[0].removeAttribute('style');
      let defaultHeigth = document.getElementsByClassName('fc-scrollgrid-sync-table') && document.getElementsByClassName('fc-scrollgrid-sync-table')[0] && document.getElementsByClassName('fc-scrollgrid-sync-table')[0].style.height?document.getElementsByClassName('fc-scrollgrid-sync-table')[0].style.height:''
      document.getElementsByClassName('fc-scrollgrid-sync-table') && document.getElementsByClassName('fc-scrollgrid-sync-table')[0].removeAttribute('style');
      if(document.getElementsByClassName('fc-timegrid-body')&& document.getElementsByClassName('fc-timegrid-body')[0]){
        // 针对周时间轴的设置
        document.getElementsByClassName('fc-timegrid-body')[0].removeAttribute('style');
        document.querySelector('.fc-timegrid-slots table').removeAttribute('style')
        document.querySelector('.fc-timegrid-cols table').removeAttribute('style')
      }
      document.getElementsByClassName('fc-scrollgrid-sync-table')[0].style.height = defaultHeigth
    },
    
    // 月视图日程过多显示样式
    moreLinkContent(arg){
      return '还有'+ arg.num +'个日程'
    },
    
    // 重新渲染日历
    renderCalendar(){
      this.calendarApi.render()
    },
    handleInputChange() {
      // 清除之前的计时器
      if (this.searchTimer) {
        clearTimeout(this.searchTimer);
      }
      
      // 输入为空时清空结果
      if (!this.searchValue.trim()) {
        this.filteredSchedules = [];
        this.showSearchResult = false;
        return;
      }
      
      // 设置新的计时器，实现防抖
      this.searchTimer = setTimeout(() => {
        this.handleSearch();
      }, 300);
    },
    
    // 执行搜索逻辑
    handleSearch() {
      if (!this.searchValue.trim()) {
        this.filteredSchedules = [];
        this.showSearchResult = false;
        return;
      }
      
      // 过滤匹配的日程
      const keyword = this.searchValue.trim().toLowerCase();
      this.filteredSchedules = this.calendarOptions.events.filter(schedule => {
        // 匹配标题
        const matchTitle = schedule.title.toLowerCase().includes(keyword);
        // 匹配描述
        const matchDesc = schedule.extendedProps.remark && 
                          schedule.extendedProps.remark.toLowerCase().includes(keyword);
        return matchTitle || matchDesc;
      });
      
      // 显示搜索结果
      this.showSearchResult = this.filteredSchedules.length > 0;
    },
    
    // 点击搜索结果中的日程
    handleScheduleClick(schedule) {
      // 隐藏搜索结果
      this.showSearchResult = false;
      
      // 跳转到该日程的日期
      this.calendarApi.gotoDate(schedule.start);
      
      // 根据日程类型切换视图
      if (this.currentType !== 'day') {
        this.currentType = 'day';
        this.toggleCurrentType();
      }
      
      // 高亮显示该日程（可以通过添加特殊样式实现）
      this.highlightSchedule(schedule.id);
      
      // 清空搜索框
      this.searchValue = '';
    },
    
    // 高亮显示指定日程
    highlightSchedule(eventId) {
      // 移除之前的高亮
      document.querySelectorAll('.fc-event-highlight').forEach(el => {
        el.classList.remove('fc-event-highlight');
      });
      
      // 添加新的高亮
      setTimeout(() => {
        const eventEl = document.querySelector(`[data-event-id="${eventId}"]`);
        if (eventEl) {
          eventEl.classList.add('fc-event-highlight');
          // 滚动到该元素
          eventEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
          
          // 3秒后移除高亮
          setTimeout(() => {
            eventEl.classList.remove('fc-event-highlight');
          }, 3000);
        }
      }, 500);
    }
  }
}
</script>

<style lang="scss" scoped>
// 头部样式
.page-layout-header {
  display: flex;
  justify-content: center;
  min-width: 760px;
  height: 66px;
  background: #fff;
  border-bottom: 1px solid #eee;
  box-shadow: 0 2px 8px 0 rgba(2, 24, 42, 0.1);
}

.page-layout-row {
  width: 1440px;
  display: flex;
  background: #fff;
  flex-direction: column;
}
.calendar-operation-box{
  .checkbox-group-item-box{
    width: 100%;
    display: flex;
    justify-content: space-between;
    margin-bottom: 4px;
    padding: 3px 10px;
    cursor: pointer;
    .op-btn{
      padding: 3px;
      border-radius: 2px;
      &:hover{
      background-color:rgba(187, 187, 187, 0.3);
      }
    }
    &:hover{
      background-color:rgba(187, 187, 187, 0.2);
    }
    &:last-child{
      margin-bottom: 0px;
    }
  }
  .checkbox-group-box{
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    overflow: hidden; /* 解决省略号不生效的问题 */
    .checkbox-wrapper {
      overflow: hidden;
      flex: 1; /* 让复选框占据剩余空间 */
    }
    .checkbox-item{
      width: 100%;
      display: flex;
      align-items: center;
      :deep(.ant-checkbox) {
        top: 0;
      }
      .checkbox-label-item{
        width: 100%;
        line-height: 1;
        display: inline-block;  //取消span格式，从而可以设置span的宽度和高度
        overflow: hidden;     // *必须设置。表示超出宽度的部分隐藏
        text-overflow: ellipsis;  // 	*必须设置。表示显示省略符号来代表被修剪的文本
        white-space: nowrap;   // *必须设置。规定段落中的文本不进行换行
      }
    }
    .hover-buttons {
      display: none;
    }
    :deep(.checkbox-item>span) {
      &:nth-child(2){
        display: inline-flex;
        width: calc(100% - 16px);
      }
    }
    .checkbox-group-item-box:hover .hover-buttons {
      display: block;
    }
    .checkbox-group-btn-box{
      white-space:nowrap;
    }
    .ant-checkbox-wrapper+.ant-checkbox-wrapper{
      margin-left:6px;
    }
    :deep(.ant-checkbox-checked) {
      .ant-checkbox-inner {
        background-color: var(--fill-color);
        border-color: var(--fill-color);
      }
    }
  }

}
.calendar-click{
  cursor: pointer;
}
.pandle-box{
  width: 100%;
}
// 月视图日程样式优化（仅月视图生效）
.eventDeal-wrap {
  &.month-view {
    max-width: 1150px;
    margin: 0 auto;
    :deep(.fc-daygrid-event) {
      margin: 0.7px 0 ;
      padding: 2px 4px ;
      margin-bottom: 4px;
      
      .fc-event-title {
        max-width: 100px;  // 根据单元格宽度调整
        white-space: nowrap;  // 不换行
        text-overflow: ellipsis;  // 长标题显示省略号
        overflow: hidden;
      }
    }
    
    // 4. 调整月视图单元格高度和与下边框距离，这里新增 padding-bottom 控制
    :deep(.fc-daygrid-day) {
      min-height: 70px ;  // 比默认增加约10px，可调整
      padding-bottom: 10px ; // 新增，设置日程与下边框距离，按需改
    }
  }
  &:not(.month-view) { 
    max-width: 1100px; // 示例宽度，可自行修改
    margin: 0 auto;
  }
}
.font-bold{
  font-weight: 600;
}

.day-list-item{
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 15px;
  background-color: rgba($color: #2097f3, $alpha: 0.1);
  border-left: 5px solid #2097f3;
  border-radius:5px;
  h3{
    font-weight: 700;
  }
  .time-gary{
    color: #666;
    flex-shrink: 0;
  }
  .day-list-item-right{
    display: flex;
    align-items: center;
    .day-list-item-right-item{
      display: flex;
      align-items: center;
    }
    .day-list-item-right-text{
      display: inline-block;
      max-width:250px; /* 定义容器宽度 */
      white-space: nowrap; /* 禁止换行 */
      overflow: hidden; /* 超出部分隐藏 */
      text-overflow: ellipsis; /* 使用省略号 */
    }
    span{
      margin-left: 10px;
    }
  }
}
.pandle-box{
  display: flex;
  width: 100%;
  height:calc(100vh - 100px);
  min-height: 670px;
  .pandle-box-right{
    width:calc(100%);
    padding: 10px;
    background: #eff3f8;
    display: flex;
    flex-direction: column;
    .CalendarBox{
      flex: 1;
      .CalendarItem{
        padding-left: 8px;
        position: relative;
        .calendar-label{
          position: absolute;
          top: -1px;
          left:-1px;
          bottom: -1px;
          width: 5px;
          z-index: 999;
          border-radius: 3px 0 0 3px;
        }
      }
    }
    .pandle-box-right-serach{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-left:80px;
      flex-wrap: wrap;
      .btn-mg{
        margin-right: 20px;
        &:last-child{
          margin-right: 50px;
        }
      }
    }
    .calendar-header-box{
      margin-bottom: 10px;
    }
    .calendar-header{
      font-size: 16px;
    }
    .calendar-header-time{
      padding: 0 15px;
    }
  }
}
.event-actions {
  margin-top: 8px;
  border-top: 1px solid #eee;
  padding-top: 8px;
  text-align: right;
}
.month-event-content {
  display: flex;
  align-items: center;
  white-space: nowrap; // 强制一行显示
  overflow: hidden;    // 超出部分隐藏
  text-overflow: ellipsis; // 长内容显示省略号
}

// 解决弹出框遮挡问题
:deep(.ant-popover) {
  z-index: 9999; /* 确保在所有元素之上 */
  
  &.month-popover {
    position: relative;
    top: 20px; /* 向下偏移 */
    
    .ant-popover-arrow {
      display: none; /* 隐藏箭头 */
    }
    
    .ant-popover-inner {
      box-shadow: 0 3px 6px -4px rgba(0, 0, 0, 0.12), 
                  0 6px 16px 0 rgba(0, 0, 0, 0.08),
                  0 9px 28px 8px rgba(0, 0, 0, 0.05); /* 增强阴影 */
    }
  }
}

// 日程项样式优化
.month-event-content {
  display: flex;
  align-items: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  
  .fc-event-title {
    max-width: 100px; /* 限制标题宽度 */
  }
  
  .fc-event-time {
    flex-shrink: 0; /* 防止时间被压缩 */
  }
}
// 搜索容器样式
.search-container {
  position: relative;
  display: inline-block;
}

// 搜索结果下拉框样式
.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  max-height: 300px;
  overflow-y: auto;
  background: #fff;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  margin-top: 4px;
  
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  
  li {
    padding: 10px 12px;
    cursor: pointer;
    transition: background 0.2s;
    
    &:hover {
      background-color: #f5f5f5;
    }
    
    &:not(:last-child) {
      border-bottom: 1px solid #f0f0f0;
    }
  }
}

// 日程标题样式
.schedule-title {
  font-weight: 500;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

// 日程时间样式
.schedule-time {
  font-size: 12px;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

// 日程高亮样式
:deep(.fc-event-highlight) {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(32, 151, 243, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(32, 151, 243, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(32, 151, 243, 0);
  }
}
</style>
