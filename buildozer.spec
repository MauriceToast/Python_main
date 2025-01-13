[app]

# (str) Title of your application
title = My Application

# (str) Package name
package.name = myapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (list) Application requirements
requirements = python3,kivy,pyjnius,firebase-admin

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# (list) Android application meta-data to set (key=value format)
android.meta_data = com.google.firebase.messaging.default_notification_icon=@mipmap/ic_launcher

# (list) Java classes to add as activities to the manifest
android.add_activities = org.kivy.android.PythonActivity

# (list) Gradle dependencies to add
android.gradle_dependencies = com.google.firebase:firebase-messaging:23.0.0

# (bool) Enable AndroidX support
android.enable_androidx = True

# (str) Android entry point, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Android Activity
android.activity_class_name = org.kivy.android.PythonActivity

# (str) Extra xml to write directly inside the <application> tag of AndroidManifest.xml
android.extra_manifest_xml = C:\Users\Admin\AndroidStudioProjects\MyApplication\app\manifests\AndroidManifest.xml

# (list) Copy these files to src/main/res/xml/ (used for example with intent-filters)
#android.res_xml = path/to/your/fcm_config.xml

version = 0.1


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
