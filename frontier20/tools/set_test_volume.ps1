param([int]$TargetProcessId, [single]$Volume = 0, [int]$WaitSeconds = 8)
$ErrorActionPreference = 'Stop'
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class HardmodeTestVolume {
    [ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")] class DeviceEnumerator {}
    [ComImport, Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IDeviceEnumerator {
        [PreserveSig] int EnumAudioEndpoints(int flow,uint state,out IntPtr devices);
        [PreserveSig] int GetDefaultAudioEndpoint(int flow,int role,out IDevice device);
    }
    [ComImport, Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IDevice {
        [PreserveSig] int Activate(ref Guid iid,uint context,IntPtr parameters,[MarshalAs(UnmanagedType.IUnknown)] out object value);
    }
    [ComImport, Guid("77AA99A0-1BD6-484F-8BC7-2C654C9A9B6F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IManager {
        [PreserveSig] int GetAudioSessionControl(IntPtr guid,uint flags,out IntPtr value);
        [PreserveSig] int GetSimpleAudioVolume(IntPtr guid,uint flags,out IntPtr value);
        [PreserveSig] int GetSessionEnumerator(out ISessions sessions);
    }
    [ComImport, Guid("E2F5BB11-0570-40CA-ACDD-3AA01277DEE8"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface ISessions {
        [PreserveSig] int GetCount(out int count);
        [PreserveSig] int GetSession(int index,out IControl session);
    }
    [ComImport, Guid("BFB7FF88-7239-4FC9-8FA2-07C950BE9C6D"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IControl {
        [PreserveSig] int GetState(out int state);
        [PreserveSig] int GetDisplayName([MarshalAs(UnmanagedType.LPWStr)] out string name);
        [PreserveSig] int SetDisplayName([MarshalAs(UnmanagedType.LPWStr)] string name,ref Guid context);
        [PreserveSig] int GetIconPath([MarshalAs(UnmanagedType.LPWStr)] out string path);
        [PreserveSig] int SetIconPath([MarshalAs(UnmanagedType.LPWStr)] string path,ref Guid context);
        [PreserveSig] int GetGroupingParam(out Guid group);
        [PreserveSig] int SetGroupingParam(ref Guid group,ref Guid context);
        [PreserveSig] int RegisterAudioSessionNotification(IntPtr callback);
        [PreserveSig] int UnregisterAudioSessionNotification(IntPtr callback);
        [PreserveSig] int GetSessionIdentifier([MarshalAs(UnmanagedType.LPWStr)] out string value);
        [PreserveSig] int GetSessionInstanceIdentifier([MarshalAs(UnmanagedType.LPWStr)] out string value);
        [PreserveSig] int GetProcessId(out uint id);
    }
    [ComImport, Guid("87CE5498-68D6-44E5-9215-6DA47EF883D8"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IVolume {
        [PreserveSig] int SetMasterVolume(float volume,ref Guid context);
        [PreserveSig] int GetMasterVolume(out float volume);
        [PreserveSig] int SetMute(bool mute,ref Guid context);
        [PreserveSig] int GetMute(out bool mute);
    }
    public static int Set(int processId,float volume) {
        int changed=0;
        var enumerator=(IDeviceEnumerator)new DeviceEnumerator();
        try {
            for(int role=0;role<3;role++) {
                IDevice device;
                if(enumerator.GetDefaultAudioEndpoint(0,role,out device)!=0) continue;
                object manager=null; ISessions sessions=null;
                try {
                    Guid iid=typeof(IManager).GUID;
                    Marshal.ThrowExceptionForHR(device.Activate(ref iid,23,IntPtr.Zero,out manager));
                    Marshal.ThrowExceptionForHR(((IManager)manager).GetSessionEnumerator(out sessions));
                    int count; sessions.GetCount(out count);
                    for(int i=0;i<count;i++) {
                        IControl control; sessions.GetSession(i,out control);
                        try {
                            uint pid; control.GetProcessId(out pid);
                            if(pid!=(uint)processId) continue;
                            var level=(IVolume)control; var context=Guid.Empty;
                            Marshal.ThrowExceptionForHR(level.SetMasterVolume(volume,ref context));
                            if(volume==0) Marshal.ThrowExceptionForHR(level.SetMute(true,ref context));
                            float readback; level.GetMasterVolume(out readback);
                            if(Math.Abs(readback-volume)>.001) throw new Exception("Audio volume readback mismatch");
                            if(volume==0) {
                                bool muted; Marshal.ThrowExceptionForHR(level.GetMute(out muted));
                                if(!muted) throw new Exception("Test audio session did not remain muted");
                            }
                            changed++;
                        } finally {Marshal.ReleaseComObject(control);}
                    }
                } finally {
                    if(sessions!=null) Marshal.ReleaseComObject(sessions);
                    if(manager!=null) Marshal.ReleaseComObject(manager);
                    Marshal.ReleaseComObject(device);
                }
            }
        } finally {Marshal.ReleaseComObject(enumerator);}
        return changed;
    }
}
'@
$deadline = [DateTime]::UtcNow.AddSeconds($WaitSeconds)
do {
    $matches = [HardmodeTestVolume]::Set($TargetProcessId, $Volume)
    if ($matches -gt 0) {
        Write-Output "Test process $TargetProcessId volume verified: $([math]::Round(100 * $Volume))%"
        exit 0
    }
    if (-not (Get-Process -Id $TargetProcessId -ErrorAction SilentlyContinue)) { exit 0 }
    Start-Sleep -Milliseconds 200
} while ([DateTime]::UtcNow -lt $deadline)
throw "No audio session appeared for test process $TargetProcessId"
