# pico_tools

pico设备测试基础工具

框架命名规则：

1.base_common —— 基础方法封装

2.general_module —— 通用模型方法加载，通用方法封装

3.pico_* —— 单项测试工具方法封装，每个代表一个专项/监控类测试

4.special_* —— 特殊方法封装，用于对特殊处理方法进行封装比如：excel处理，log分析等等

5.tools_index —— 主方法，主页面封装，加载所有分页面，直接打包方法

集成工具打包方法：

1.工具静默无感自升级，需要在服务器上传更新包

2.在本地打包通过引入python库：nuitka，外部创建main.py,并在外层控制台执行： 
    
工具打应用包（正式版）指令： 

nuitka --standalone --show-memory --show-progress --output-dir=out --enable-plugin=tk-inter --windows-disable-console --nofollow-imports  --follow-import-to=pico_tools --windows-icon-from-ico=./tool.ico .\main.py 
    
工具打测试包（带调试窗口）指令：  

nuitka --standalone --show-memory --show-progress --output-dir=out --enable-plugin=tk-inter --nofollow-imports  --follow-import-to=pico_tools --windows-icon-from-ico=./tool.ico .\main.py
  