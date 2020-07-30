# WizIO 2019 Georgi Angelov
#   http://www.wizio.eu/
#   https://github.com/Wiz-IO

# openssl ---> sudo apt-get install libssl-dev

import os
import subprocess
from os.path import join
from shutil import copyfile
from SCons.Script import ARGUMENTS, DefaultEnvironment, Builder

def run_application(target, source, env):   
    subprocess.call(['xterm', '-e', join(env.get("BUILD_DIR"), "program")])

def init_compiler(env):
    env.Replace(
        BUILD_DIR = env.subst("$BUILD_DIR").replace("\\", "/"),
        AR="ar",
        AS="as",
        CC="gcc",
        GDB="gdb",
        CXX="g++",
        OBJCOPY="objcopy",
        RANLIB="ranlib",
        SIZETOOL="size",
        ARFLAGS=["rc"],
        SIZEPROGREGEXP=r"^(?:\.text|\.data|\.bootloader)\s+(\d+).*",
        SIZEDATAREGEXP=r"^(?:\.data|\.bss|\.noinit)\s+(\d+).*",
        SIZECHECKCMD="$SIZETOOL -A -d $SOURCES",
        SIZEPRINTCMD='$SIZETOOL --mcu=$BOARD_MCU -C -d $SOURCES',
        PROGSUFFIX="",  
    )

def dev_init(env, platform):
    print("Running dev_init on teensy-ownposix.py")
    print(env.PioPlatform())
    init_compiler(env)
    platform_mimic = "arduino"
    framework_dir = env.PioPlatform().get_package_dir("framework-wizio-zusoro")
    #framework_dir = env.PioPlatform().get_package_dir("framework-wizioteensy")
    print(f"Nr 1: {framework_dir}") 
    #framework_dir= "/home/gabo/.platformio/packages/framework-wizioteensy"
    #print(f"Nr 2: {framework_dir}") 
    variant = env.BoardConfig().get("build.variant")   
    core = env.get("PLATFORM") # posix    
    env.Append(
       CPPDEFINES = [ # -D 
            "{}=200".format(platform.upper()), 
            "CORE_" + core.upper().replace("-", "_"),
        ],        
        CPPPATH = [ # -I
            join(framework_dir,  platform, platform_mimic),
            join(framework_dir,  platform, "cores", core),
            join(framework_dir,  platform, "variants", variant),      
            join("$PROJECT_DIR"),         
            join("$PROJECT_DIR", "lib"),
            join("$PROJECT_DIR", "include")       
        ],        
        CFLAGS = [        
            "-Wno-pointer-sign",      
        ],
        CXXFLAGS = [                               
            "-fno-rtti",
            "-fno-exceptions", 
            "-fno-non-call-exceptions",
            "-fno-use-cxa-atexit",
            "-fno-threadsafe-statics",
        ],    
        CCFLAGS = [
            "-Os", "-g",                                
            "-fdata-sections",      
            "-ffunction-sections",
            "-fno-strict-aliasing",
            #"-fsingle-precision-constant",             
            "-Wall", 
            "-Wstrict-prototypes", 
            "-Wp,-w",       
               
        ],        
        LINKFLAGS = [                                                                 
            "-Wl,--gc-sections",            
        ],    
        LIBPATH = [],      
        LIBS = [                 
            "libcrypto", # openssl
            "libssl",
        ],     
        LIBSOURCE_DIRS = [ 
            join(framework_dir, platform, "libraries"),             
        ],   
        UPLOADCMD = run_application 
    )
    print(F"Path: {framework_dir}\n Platform: {platform}\n Core: {core}\n Variant: {variant}")
    libs = []
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_" + platform),
            join(framework_dir, platform, platform_mimic),
    ))    
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_core"),
            join(framework_dir, platform, "cores", core),
    ))    
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_variant"),
            join(framework_dir, platform, "variants", variant),
    ))            
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_custom_lib"), 
            join("$PROJECT_DIR", "lib"),                       
    ))           
    env.Append(LIBS = libs)   
