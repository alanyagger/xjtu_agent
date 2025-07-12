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
          <a-button 
            class='btn-mg' 
            @click="refreshSchedules"
          >
            刷新
          </a-button>
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
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from "@fullcalendar/interaction";
import timeGridPlugin from "@fullcalendar/timegrid";
import zhLocale from "@fullcalendar/core/locales/zh-cn";
import dayjs from 'dayjs';
import { LeftOutlined, RightOutlined, PlusOutlined, SyncOutlined } from '@ant-design/icons-vue';
import { Spin } from 'ant-design-vue';
import { getToken } from "@/utils/auth.ts";
import { h } from 'vue';

export default {
  name: 'CalendarView',
  components: {
    FullCalendar,
    LeftOutlined,
    RightOutlined,
    PlusOutlined,
    SyncOutlined,
    HeaderView,
    Spin
  },
  data() {
    return {
      dayjs,
      searchValue: '',
      filteredSchedules: [],
      showSearchResult: false,
      searchTimer: null,
      currentType: 'month',
      currentDefaultType: 'month',
      currentTime: dayjs(),
      calendarApi: null,
      currentTimeShow: null,
      deleteConfirmVisible: false,
      eventToDelete: null,
      calendarOptions: {
        plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
        initialView: 'dayGridMonth',
        headerToolbar: false,
        firstDay: '1',
        locales: [zhLocale],
        handleWindowResize: true,
        locale: "zh-cn",
        weekNumberCalculation: 'ISO',
        eventColor: '#3d8eec',
        timeGridEventMinHeight: '20',
        aspectRatio: '2',
        height: '100%',
        fixedWeekCount: false,
        events: [],
        eventTimeFormat: {
          hour: '2-digit',
          minute: '2-digit',
          meridiem: false,
          hour12: false
        },
        editable: false,
        selectable: true,
        selectMirror: true,
        selectMinDistance: 0,
        dayMaxEventRows: 4,
        moreLinkContent: this.moreLinkContent,
        weekends: true,
        navLinks: false,
        selectHelper: false,
        selectEventOverlap: false,
        nowIndicator: true,
        select: this.handleDateClick,
        eventsSet: this.handleEvents,
        eventClick: this.handleEventClick,
        eventResize: this.onEventResize,
      },
      addModalVisible: false,
      newSchedule: {
        title: '',
        start: dayjs(),
        end: dayjs().add(1, 'hour'),
        description: '',
        color: '#2097f3',
      },
      loading: false,
      apiBaseUrl: 'http://localhost:8000/api',
      currentUser: {
        username: localStorage.getItem('username') || ''
      },
      loadingRefresh: false,
      isFetchingSchedules: false,
      searchDebounceTime: 800,
      cachedSearchResults: {},
      // 新增：上次加载时间和缓存有效期（毫秒）
      lastLoadTime: 0,
      cacheValidDuration: 600000, // 1分钟
    };
  },
  mounted() {
    this.calendarApi = this.$refs.calendarRef.getApi();
    this.currentTimeShow = dayjs(this.currentTime).format('YYYY 年 MM 月');
    document.querySelector('.eventDeal-wrap')?.classList.add('month-view');
    document.addEventListener('click', (e) => {
      const searchContainer = document.querySelector('.search-container');
      if (searchContainer && !searchContainer.contains(e.target)) {
        this.showSearchResult = false;
      }
    });
    
    // 检查本地缓存
    const cached = localStorage.getItem(`schedules_${this.currentUser.username}`);
    if (cached) {
      // 如果有缓存，先加载缓存数据
      this.processScheduleData(JSON.parse(cached));
      // 再异步检查更新
      setTimeout(() => this.checkScheduleUpdate(), 100);
    } else {
      // 没有缓存则直接加载
      this.checkLoginStatus();
    }
  },
  methods: {
    // 检查登录状态
    checkLoginStatus() {
      const token = getToken();
      const username = localStorage.getItem('username');
      
      if (!token || !username) {
        this.$message.warning('请先登录以查看您的日程');
        return false;
      }
      
      this.currentUser.username = username;
      // 检查缓存是否有效
      const now = Date.now();
      const lastLoadTime = localStorage.getItem(`lastLoadTime_${this.currentUser.username}`);
      
      if (lastLoadTime && (now - parseInt(lastLoadTime) < this.cacheValidDuration)) {
        // 缓存有效，从本地加载
        const cached = localStorage.getItem(`schedules_${this.currentUser.username}`);
        if (cached) {
          this.processScheduleData(JSON.parse(cached));
          return true;
        }
      }
      
      // 缓存无效或不存在，重新加载
      this.getScheduleList();
      return true;
    },

    // 获取认证头
    getAuthHeaders() {
      const token = getToken();
      return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      };
    },
    
    // 检查日程更新（后台异步）
    async checkScheduleUpdate() {
      try {
        // 打印即将发送的认证头
        const authHeaders = this.getAuthHeaders();
        console.log('Auth Headers:', authHeaders);

        const response = await fetch(`${this.apiBaseUrl}/schedules/last-updated/`, {
          method: 'GET',
          headers: authHeaders
        });

        console.log('Checking for schedule updates...', authHeaders);

        console.log('Checking for schedule updates...', response);
        
        if (!response.ok) throw new Error('检查更新失败');
        
        const lastUpdated = await response.json();
        const localLastUpdated = localStorage.getItem(`lastUpdated_${this.currentUser.username}`);
        
        if (!localLastUpdated || lastUpdated.timestamp > localLastUpdated) {
          // 有更新，刷新数据
          this.getScheduleList();
          localStorage.setItem(`lastUpdated_${this.currentUser.username}`, lastUpdated.timestamp);
        }
      } catch (error) {
        console.error('检查更新失败:', error);
      }
    },
    
    // 获取日程列表
async getScheduleList(forceRefresh = false) {
  // 添加调用标志，防止循环调用
  if (this.isFetchingSchedules) return;
  this.isFetchingSchedules = true;

  try {
    if (!this.checkLoginStatus()) return;

    // 检查缓存是否存在且在有效期内（默认10分钟）
    const cacheKey = `schedules_${this.currentUser.username}`;
    const timeKey = `lastLoadTime_${this.currentUser.username}`;
    const cacheValidDuration = 10 * 60 * 1000; // 10分钟

    const cachedData = localStorage.getItem(cacheKey);
    const lastLoadTime = localStorage.getItem(timeKey);
    
    // 修复缓存有效性检查逻辑
    const isCacheValid = cachedData && 
                        lastLoadTime && 
                        (Date.now() - parseInt(lastLoadTime)) < cacheValidDuration;

    // 使用有效缓存，不请求后台
    if (isCacheValid && !forceRefresh) {
      this.processScheduleData(JSON.parse(cachedData));
      this.lastLoadTime = parseInt(lastLoadTime);
      return JSON.parse(cachedData);
    }

    // 否则请求后台数据
    this.loading = true;
    try {
      const response = await fetch(`${this.apiBaseUrl}/schedules/`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      });

      console.log('Fetching schedules from API...', response);
    
      if (!response.ok) throw new Error('获取日程失败');
    
      const scheduleList = await response.json();
      console.log('Fetched schedule list:', scheduleList);
      this.processScheduleData(scheduleList);
    
      // 更新缓存数据和加载时间
      localStorage.setItem(cacheKey, JSON.stringify(scheduleList));
      localStorage.setItem(timeKey, Date.now().toString());
      this.lastLoadTime = Date.now();
      return scheduleList;
    } catch (error) {
      console.error('获取日程失败:', error);
      this.$message.error('获取日程失败，尝试加载本地缓存');
    
      if (cachedData) {
        this.processScheduleData(JSON.parse(cachedData));
      } else {
        this.calendarOptions.events = [];
        this.$message.info('暂无日程数据');
      }
      throw error;
    } finally {
      this.loading = false;
    }
  } finally {
    // 重置调用标志
    this.isFetchingSchedules = false;
  }},

    // 处理日程数据
    processScheduleData(scheduleList) {
      this.calendarOptions.events = scheduleList.map((item) => {
        const isCrossDay = this.isCrossDay(item.start_time, item.end_time);
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
          textColor: '#fff',
          className: dayjs(item.end_time).isBefore(dayjs()) ? "text-normal-gary" : "text-normal",
          extendedProps: {
            start: dayjs(item.start_time).format('YYYY-MM-DD HH:mm'),
            end_time: dayjs(item.end_time).format('YYYY-MM-DD HH:mm'),
            remark: item.remark || '',
            schcolor: item.color || '',
            calendarColor: item.schedule_calendar?.color || '',
            displayTime: displayTime
          }
        };
      });
      
      setTimeout(() => {
        this.autoScaleFullCalendar();
      }, 1000);
    },
    
    // 新增日程
    async handleAddSchedule() {
      if (!this.newSchedule.title.trim()) {
        this.$message.error('请输入日程标题');
        return;
      }
      
      if (this.newSchedule.end.isBefore(this.newSchedule.start)) {
        this.$message.error('结束时间不能早于开始时间');
        return;
      }
      
      const loadingInstance = this.$message.loading('正在创建日程...', 0);
      
      try {
        const scheduleData = {
          name: this.newSchedule.title,
          start_time: this.newSchedule.start.format('YYYY-MM-DDTHH:mm:00'),
          end_time: this.newSchedule.end.format('YYYY-MM-DDTHH:mm:00'),
          color: this.newSchedule.color,
          remark: this.newSchedule.description
        };
        
        const response = await fetch(`${this.apiBaseUrl}/schedules/`, {
          method: 'POST',
          headers: this.getAuthHeaders(),
          body: JSON.stringify(scheduleData)
        });
        
        if (!response.ok) throw new Error('创建日程失败');
        
        this.addModalVisible = false;
        loadingInstance();
        this.$message.success('日程创建成功！');
        const newSchedule = await response.json();

        // 更新本地缓存
        this.updateLocalCache(newSchedule);
    
        // 无需刷新整个列表，直接添加到前端显示
        this.processScheduleData([newSchedule], true);
        
        // 刷新数据
        this.refreshSchedules();
      } catch (error) {
        loadingInstance();
        this.$message.error('创建日程失败：' + error.message);
        console.error('创建日程出错:', error);
      }
    },

    // 更新本地缓存
    updateLocalCache(newSchedule) {
      const cacheKey = `schedules_${this.currentUser.username}`;
      const cachedData = localStorage.getItem(cacheKey);
  
      if (cachedData) {
        const schedules = JSON.parse(cachedData);
        schedules.push(newSchedule);
    
        // 按开始时间排序
        schedules.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
    
        localStorage.setItem(cacheKey, JSON.stringify(schedules));
      } else {
        // 如果没有缓存，创建新缓存
        localStorage.setItem(cacheKey, JSON.stringify([newSchedule]));
      }
  
      // 更新最后加载时间
      const timeKey = `lastLoadTime_${this.currentUser.username}`;
      localStorage.setItem(timeKey, Date.now().toString());
    },
    
    // 删除日程
    async confirmDelete() {
      if (!this.eventToDelete) {
        this.deleteConfirmVisible = false;
        return;
      }
      
      this.loading = true;
      try {
        const response = await fetch(`${this.apiBaseUrl}/schedules/${this.eventToDelete}`, {
          method: 'DELETE',
          headers: this.getAuthHeaders()
        });
        
        if (!response.ok) throw new Error('删除日程失败');
        
        this.$message.success('日程已成功删除');
        this.refreshSchedules();
      } catch (error) {
        this.$message.error('删除日程失败：' + error.message);
        console.error('删除日程出错:', error);
      } finally {
        this.loading = false;
        this.deleteConfirmVisible = false;
        this.eventToDelete = null;
      }
    },
    
    // 搜索功能
    async handleSearch() {
      if (!this.searchValue.trim()) {
        this.filteredSchedules = [];
        this.showSearchResult = false;
        return;
      }
      
      const keyword = this.searchValue.trim().toLowerCase();
      
      // 检查缓存
      if (this.cachedSearchResults[keyword]) {
        this.filteredSchedules = this.cachedSearchResults[keyword];
        this.showSearchResult = this.filteredSchedules.length > 0;
        return;
      }
      
      this.loading = true;
      try {
        const encodedKeyword = encodeURIComponent(keyword);
        const response = await fetch(`${this.apiBaseUrl}/schedules/search/?keyword=${encodedKeyword}`, {
          method: 'GET',
          headers: this.getAuthHeaders()
        });
        
        if (!response.ok) throw new Error('搜索日程失败');
        
        const searchResults = await response.json();
        
        const formattedResults = searchResults.map(schedule => {
          const isCrossDay = this.isCrossDay(schedule.start_time, schedule.end_time);
          return {
            id: schedule.id,
            title: schedule.name,
            backgroundColor: schedule.color || '#2097f3',
            extendedProps: {
              start: dayjs(schedule.start_time).format('YYYY-MM-DD HH:mm'),
              end_time: dayjs(schedule.end_time).format('YYYY-MM-DD HH:mm')
            }
          };
        });
        
        // 缓存搜索结果（10分钟有效期）
        this.cachedSearchResults[keyword] = formattedResults;
        setTimeout(() => {
          delete this.cachedSearchResults[keyword];
        }, 600000);
        
        this.filteredSchedules = formattedResults;
        this.showSearchResult = this.filteredSchedules.length > 0;
      } catch (error) {
        this.$message.error('搜索日程失败：' + error.message);
        console.error('搜索日程出错:', error);
        this.localSearch();
      } finally {
        this.loading = false;
      }
    },
    
    // 本地搜索（API失败时的降级方案）
    localSearch() {
      const keyword = this.searchValue.trim().toLowerCase();
      this.filteredSchedules = this.calendarOptions.events.filter(schedule => {
        const matchTitle = schedule.title.toLowerCase().includes(keyword);
        const matchDesc = schedule.extendedProps.remark && 
                          schedule.extendedProps.remark.toLowerCase().includes(keyword);
        return matchTitle || matchDesc;
      });
      
      this.showSearchResult = this.filteredSchedules.length > 0;
    },
    
    // 手动刷新日程
    async refreshSchedules() {
      if (this.loadingRefresh) return;
      
      this.loadingRefresh = true;
      try {
        //await this.checkScheduleUpdate();
        await this.getScheduleList(true);
        this.$message.success('日程已刷新');
      } catch (error) {
        console.error('刷新日程失败:', error);
        this.$message.error('刷新失败，请重试');
      } finally {
        this.loadingRefresh = false;
      }
    },
    
    // 搜索输入变化处理
    handleInputChange() {
      if (this.searchTimer) {
        clearTimeout(this.searchTimer);
      }
      
      if (!this.searchValue.trim()) {
        this.filteredSchedules = [];
        this.showSearchResult = false;
        return;
      }
      
      this.searchTimer = setTimeout(() => {
        this.handleSearch();
      }, this.searchDebounceTime);
    },
    
    // 判断是否跨天
    isCrossDay(startTime, endTime) {
      return dayjs(startTime).format('YYYY-MM-DD') !== dayjs(endTime).format('YYYY-MM-DD');
    },
    
    // 处理删除事件
    handleDeleteEvent(eventId) {
      this.eventToDelete = eventId;
      this.deleteConfirmVisible = true;
    },
    
    // 点击日程事件
    handleEventClick(clickInfo) {
      console.log(clickInfo, 'event');
    },
    
    // 返回至当前日期
    setCurrentTime() {
      this.currentTime = dayjs();
      this.calendarApi.today();
      
      if (this.currentType === 'day') {
        this.currentTimeShow = dayjs(this.currentTime).format('YYYY年MM月DD日');
      } else if (this.currentType === 'week') {
        this.currentTimeShow = this.calendarApi.view.title;
      } else {
        this.currentTimeShow = dayjs(this.currentTime).format('YYYY 年 MM 月');
      }
    },
    
    // 日程视图切换
    toggleCurrentType() {
      const calendarWrap = document.querySelector('.eventDeal-wrap');
      if (this.currentType == 'week') {
        this.$nextTick(function() {
          this.calendarApi = this.$refs.calendarRef.getApi();
          this.calendarApi.gotoDate(dayjs(this.currentTime).format('YYYY-MM-DD HH:mm'));
          this.changePanelShow('timeGridWeek');
          calendarWrap?.classList.remove('month-view');
        });
      } else if (this.currentType == 'month') {
        this.$nextTick(() => {
          this.calendarApi = this.$refs.calendarRef.getApi();
          this.calendarApi.gotoDate(dayjs(this.currentTime).format('YYYY-MM-DD HH:mm'));
          this.changePanelShow('dayGridMonth');
          calendarWrap?.classList.add('month-view');
        });
      } else {
        this.$nextTick(() => {
          this.calendarApi = this.$refs.calendarRef.getApi();
          this.calendarApi.gotoDate(dayjs(this.currentTime).format('YYYY-MM-DD HH:mm'));
          this.changePanelShow('timeGridDay');
          this.currentTimeShow = dayjs(this.currentTime).format('YYYY年MM月DD日');
          calendarWrap?.classList.remove('month-view');
        });
      }
    },
    
    // 更改面板显示类型
    changePanelShow(type) {
      this.calendarApi.changeView(type);
    },
    
    // 时间导航
    handleChangeTime(type) {
      let changeTime = null;
      if (type == 'prive') {
        changeTime = dayjs(this.currentTime).subtract(1, this.currentType);
      } else {
        changeTime = dayjs(this.currentTime).add(1, this.currentType);
      }
      
      this.currentTime = changeTime;
      this.currentTimeShow = this.currentType == 'day' 
        ? dayjs(this.currentTime).format('YYYY年MM月DD日') 
        : (this.currentType == 'week' 
          ? this.calendarApi.view.title 
          : dayjs(this.currentTime).format('YYYY 年 MM 月'));
      
      this.calendarApi.gotoDate(dayjs(changeTime).format('YYYY-MM-DD HH:mm'));
    },
    
    // 自适应大小调整
    autoScaleFullCalendar() {
      document.getElementsByClassName('fc-col-header') && document.getElementsByClassName('fc-col-header')[0].removeAttribute('style');
      document.getElementsByClassName('fc-daygrid-body') && document.getElementsByClassName('fc-daygrid-body')[0].removeAttribute('style');
      let defaultHeigth = document.getElementsByClassName('fc-scrollgrid-sync-table') && document.getElementsByClassName('fc-scrollgrid-sync-table')[0] && document.getElementsByClassName('fc-scrollgrid-sync-table')[0].style.height?document.getElementsByClassName('fc-scrollgrid-sync-table')[0].style.height:'';
      document.getElementsByClassName('fc-scrollgrid-sync-table') && document.getElementsByClassName('fc-scrollgrid-sync-table')[0].removeAttribute('style');
      
      if (document.getElementsByClassName('fc-timegrid-body') && document.getElementsByClassName('fc-timegrid-body')[0]) {
        document.getElementsByClassName('fc-timegrid-body')[0].removeAttribute('style');
        document.querySelector('.fc-timegrid-slots table').removeAttribute('style');
        document.querySelector('.fc-timegrid-cols table').removeAttribute('style');
      }
      
      document.getElementsByClassName('fc-scrollgrid-sync-table')[0].style.height = defaultHeigth;
    },
    
    // 月视图日程过多显示样式
    moreLinkContent(arg) {
      return '还有' + arg.num + '个日程';
    },
    
    // 重新渲染日历
    renderCalendar() {
      this.calendarApi.render();
    },
    
    // 点击搜索结果中的日程
    handleScheduleClick(schedule) {
      this.showSearchResult = false;
      this.calendarApi.gotoDate(schedule.start);
      
      if (this.currentType !== 'day') {
        this.currentType = 'day';
        this.toggleCurrentType();
      }
      
      this.highlightSchedule(schedule.id);
      this.searchValue = '';
    },
    
    // 高亮显示指定日程
    highlightSchedule(eventId) {
      document.querySelectorAll('.fc-event-highlight').forEach(el => {
        el.classList.remove('fc-event-highlight');
      });
      
      setTimeout(() => {
        const eventEl = document.querySelector(`[data-event-id="${eventId}"]`);
        if (eventEl) {
          eventEl.classList.add('fc-event-highlight');
          eventEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
          
          setTimeout(() => {
            eventEl.classList.remove('fc-event-highlight');
          }, 3000);
        }
      }, 500);
    },
    
    // 处理开始时间变化
    handleStartTimeChange(date) {
      // 确保结束时间不早于开始时间
      if (date && this.newSchedule.end.isBefore(date)) {
        this.newSchedule.end = dayjs(date).add(1, 'hour');
      }
    },
    
    // 处理日期选择
    handleDateClick(info) {
      this.addModalVisible = true;
      this.newSchedule.start = dayjs(info.startStr);
      this.newSchedule.end = dayjs(info.startStr).add(1, 'hour');
    },
    
    // 处理事件加载完成
    handleEvents(events) {
      // 日历事件加载完成后的回调
    },
    
    // 处理事件调整
    onEventResize(eventInfo) {
      // 事件大小调整后的回调
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

// 刷新按钮样式优化
:deep(.ant-btn-icon-only) {
  margin-right: 10px;
  border-radius: 4px;
}
</style>