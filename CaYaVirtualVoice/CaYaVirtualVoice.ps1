# CaYa Virtual Voice 1.0.1
# Windows 10/11 - Windows PowerShell 5.1

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

try {
    Add-Type -AssemblyName PresentationFramework
    Add-Type -AssemblyName PresentationCore
    Add-Type -AssemblyName WindowsBase
}
catch {
    Add-Type -AssemblyName System.Windows.Forms -ErrorAction SilentlyContinue
    [System.Windows.Forms.MessageBox]::Show(
        "Windows arayüz bileşenleri yüklenemedi.`r`n`r`n$($_.Exception.Message)",
        'CaYa Virtual Voice', 'OK', 'Error'
    ) | Out-Null
    exit 1
}

function Show-AppError {
    param([string]$Message)
    [System.Windows.MessageBox]::Show($Message, 'CaYa Virtual Voice', 'OK', 'Error') | Out-Null
}

# System.Speech.dll kullanılmaz. Windows'ta yerleşik bulunan SAPI 5 COM bileşeni kullanılır.
try {
    $script:Sapi = New-Object -ComObject 'SAPI.SpVoice'
}
catch {
    Show-AppError "Windows konuşma bileşeni (SAPI.SpVoice) başlatılamadı.`r`n`r`n$($_.Exception.Message)"
    exit 1
}

[xml]$xaml = @'
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="CaYa Virtual Voice 1.0.1" Width="820" Height="670"
        MinWidth="680" MinHeight="570" WindowStartupLocation="CenterScreen"
        Background="#0B1018" Foreground="#EEF4FF" FontFamily="Segoe UI"
        ResizeMode="CanResize">
    <Window.Resources>
        <Style TargetType="TextBlock">
            <Setter Property="Foreground" Value="#DCE8F8"/>
        </Style>
        <Style TargetType="Button">
            <Setter Property="Foreground" Value="#F7FBFF"/>
            <Setter Property="Background" Value="#1B2A3E"/>
            <Setter Property="BorderBrush" Value="#36516E"/>
            <Setter Property="Padding" Value="15,9"/>
            <Setter Property="Margin" Value="0,0,8,0"/>
            <Setter Property="Cursor" Value="Hand"/>
            <Setter Property="FontWeight" Value="SemiBold"/>
        </Style>
        <Style TargetType="ComboBox">
            <Setter Property="Foreground" Value="#111827"/>
            <Setter Property="Background" Value="#F5F8FC"/>
            <Setter Property="Padding" Value="8,6"/>
            <Setter Property="Margin" Value="0,5,0,0"/>
        </Style>
        <Style TargetType="Slider">
            <Setter Property="Margin" Value="0,8,0,0"/>
        </Style>
        <Style x:Key="Card" TargetType="Border">
            <Setter Property="Background" Value="#121B28"/>
            <Setter Property="BorderBrush" Value="#24364C"/>
            <Setter Property="BorderThickness" Value="1"/>
            <Setter Property="CornerRadius" Value="12"/>
            <Setter Property="Padding" Value="16"/>
        </Style>
    </Window.Resources>

    <Grid Margin="24">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>

        <Grid Grid.Row="0" Margin="0,0,0,18">
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="*"/>
                <ColumnDefinition Width="Auto"/>
            </Grid.ColumnDefinitions>
            <StackPanel>
                <TextBlock Text="CaYa Virtual Voice" FontSize="28" FontWeight="Bold" Foreground="#F7FBFF"/>
                <TextBlock Text="Yazdığın metni seçtiğin sanal ses kablosuna gönderir." Margin="0,4,0,0" Foreground="#8FA5BE"/>
            </StackPanel>
            <CheckBox x:Name="AlwaysOnTopCheck" Grid.Column="1" Content="Her zaman üstte"
                      VerticalAlignment="Center" Foreground="#BED0E5"/>
        </Grid>

        <Border Grid.Row="1" Style="{StaticResource Card}" Margin="0,0,0,14">
            <Grid>
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="3*"/>
                    <ColumnDefinition Width="12"/>
                    <ColumnDefinition Width="2*"/>
                </Grid.ColumnDefinitions>
                <StackPanel Grid.Column="0">
                    <DockPanel LastChildFill="True">
                        <Button x:Name="RefreshButton" DockPanel.Dock="Right" Content="Yenile"
                                Padding="11,5" Margin="8,0,0,0"/>
                        <TextBlock Text="Ses çıkışı / sanal kablo" FontWeight="SemiBold" VerticalAlignment="Center"/>
                    </DockPanel>
                    <ComboBox x:Name="DeviceCombo" DisplayMemberPath="Name"/>
                    <TextBlock Text="VB-CABLE: burada CABLE Input, Discord'da mikrofon olarak CABLE Output seçilir."
                               FontSize="11" Foreground="#7890AA" Margin="0,5,0,0" TextWrapping="Wrap"/>
                </StackPanel>
                <StackPanel Grid.Column="2">
                    <TextBlock Text="Konuşma sesi" FontWeight="SemiBold"/>
                    <ComboBox x:Name="VoiceCombo" DisplayMemberPath="Name"/>
                    <TextBlock x:Name="VoiceHint" Text="Türkçe ses yoksa Windows Dil ve Konuşma ayarlarından eklenebilir."
                               FontSize="11" Foreground="#7890AA" Margin="0,5,0,0" TextWrapping="Wrap"/>
                </StackPanel>
            </Grid>
        </Border>

        <Border Grid.Row="2" Style="{StaticResource Card}" Margin="0,0,0,14">
            <Grid>
                <Grid.RowDefinitions>
                    <RowDefinition Height="Auto"/>
                    <RowDefinition Height="*"/>
                    <RowDefinition Height="Auto"/>
                </Grid.RowDefinitions>
                <DockPanel Grid.Row="0" Margin="0,0,0,9">
                    <TextBlock x:Name="CharCount" DockPanel.Dock="Right" Text="0 karakter" Foreground="#7890AA"/>
                    <TextBlock Text="Okunacak metin" FontWeight="SemiBold"/>
                </DockPanel>
                <TextBox x:Name="TextInput" Grid.Row="1" AcceptsReturn="True" TextWrapping="Wrap"
                         VerticalScrollBarVisibility="Auto" Background="#0A111C" Foreground="#F2F7FF"
                         BorderBrush="#2C425D" BorderThickness="1" Padding="14" FontSize="17"
                         SpellCheck.IsEnabled="True"
                         Text="Merhaba! Bu metin seçtiğin sanal ses kablosundan okunacak."/>
                <TextBlock Grid.Row="2" Text="Konuş: Ctrl + Enter   •   Durdur: Escape"
                           FontSize="11" Foreground="#7890AA" Margin="0,7,0,0"/>
            </Grid>
        </Border>

        <Border Grid.Row="3" Style="{StaticResource Card}" Margin="0,0,0,14">
            <Grid>
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*"/>
                    <ColumnDefinition Width="24"/>
                    <ColumnDefinition Width="*"/>
                </Grid.ColumnDefinitions>
                <StackPanel Grid.Column="0">
                    <DockPanel>
                        <TextBlock Text="Konuşma hızı" FontWeight="SemiBold"/>
                        <TextBlock x:Name="RateValue" Text="0" HorizontalAlignment="Right" Foreground="#8FA5BE"/>
                    </DockPanel>
                    <Slider x:Name="RateSlider" Minimum="-10" Maximum="10" Value="0"
                            TickFrequency="1" IsSnapToTickEnabled="True"/>
                </StackPanel>
                <StackPanel Grid.Column="2">
                    <DockPanel>
                        <TextBlock Text="Ses seviyesi" FontWeight="SemiBold"/>
                        <TextBlock x:Name="VolumeValue" Text="100%" HorizontalAlignment="Right" Foreground="#8FA5BE"/>
                    </DockPanel>
                    <Slider x:Name="VolumeSlider" Minimum="0" Maximum="100" Value="100"
                            TickFrequency="5" IsSnapToTickEnabled="True"/>
                </StackPanel>
            </Grid>
        </Border>

        <Grid Grid.Row="4">
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="Auto"/>
                <ColumnDefinition Width="*"/>
                <ColumnDefinition Width="Auto"/>
            </Grid.ColumnDefinitions>
            <StackPanel Orientation="Horizontal">
                <Button x:Name="SpeakButton" Content="▶  Konuş" Background="#176BCE"
                        BorderBrush="#3187E8" Padding="22,10"/>
                <Button x:Name="StopButton" Content="■  Durdur"/>
                <Button x:Name="ClearButton" Content="Temizle"/>
            </StackPanel>
            <Border Grid.Column="1" Background="#101A27" BorderBrush="#23364D"
                    BorderThickness="1" CornerRadius="9" Padding="13,8" Margin="8,0,8,0">
                <StackPanel Orientation="Horizontal" VerticalAlignment="Center">
                    <Ellipse x:Name="StatusDot" Width="9" Height="9" Fill="#58C97A" Margin="0,0,8,0"/>
                    <TextBlock x:Name="StatusText" Text="Hazır" VerticalAlignment="Center" Foreground="#BFD0E5"/>
                </StackPanel>
            </Border>
            <Button x:Name="SpeechSettingsButton" Grid.Column="2" Content="Windows ses ayarları" Margin="0"/>
        </Grid>
    </Grid>
</Window>
'@

try {
    $reader = New-Object System.Xml.XmlNodeReader $xaml
    $window = [Windows.Markup.XamlReader]::Load($reader)
}
catch {
    Show-AppError "Uygulama arayüzü açılamadı.`r`n`r`n$($_.Exception.Message)"
    exit 1
}

$controlNames = @(
    'AlwaysOnTopCheck','RefreshButton','DeviceCombo','VoiceCombo','VoiceHint','TextInput','CharCount',
    'RateSlider','RateValue','VolumeSlider','VolumeValue','SpeakButton','StopButton','ClearButton',
    'StatusText','StatusDot','SpeechSettingsButton'
)
foreach ($controlName in $controlNames) {
    Set-Variable -Name $controlName -Value $window.FindName($controlName) -Scope Script
}

$settingsDir = Join-Path $env:APPDATA 'CaYaVirtualVoice'
$settingsFile = Join-Path $settingsDir 'settings.json'
$script:IsSpeaking = $false
$script:LastSpeakError = ''

function Get-TokenDescription {
    param($Token)
    try { return [string]$Token.GetDescription() }
    catch {
        try { return [string]$Token.GetDescription(0) }
        catch { return 'Adsız aygıt' }
    }
}

function Get-TokenId {
    param($Token)
    try { return [string]$Token.Id }
    catch { return (Get-TokenDescription $Token) }
}

function Load-Devices {
    $previousId = $null
    if ($DeviceCombo.SelectedItem) { $previousId = [string]$DeviceCombo.SelectedItem.Id }

    $items = New-Object 'System.Collections.ObjectModel.ObservableCollection[object]'
    $items.Add([pscustomobject]@{ Name = 'Windows varsayılan ses çıkışı'; Id = '__DEFAULT__'; Token = $null })

    try {
        $tokens = $script:Sapi.GetAudioOutputs('', '')
        for ($i = 0; $i -lt [int]$tokens.Count; $i++) {
            $token = $tokens.Item($i)
            $name = Get-TokenDescription $token
            $id = Get-TokenId $token
            $items.Add([pscustomobject]@{ Name = $name; Id = $id; Token = $token })
        }
    }
    catch {
        Show-AppError "Ses çıkışları okunamadı.`r`n`r`n$($_.Exception.Message)"
    }

    $DeviceCombo.ItemsSource = $items
    $targetIndex = 0
    for ($i = 0; $i -lt $items.Count; $i++) {
        if ($previousId -and $items[$i].Id -eq $previousId) {
            $targetIndex = $i
            break
        }
        if (-not $previousId -and $items[$i].Name -match '(?i)CABLE Input|Virtual Cable|VoiceMeeter Input|Line 1') {
            $targetIndex = $i
        }
    }
    if ($items.Count -gt 0) { $DeviceCombo.SelectedIndex = $targetIndex }
}

function Load-Voices {
    $previousId = $null
    if ($VoiceCombo.SelectedItem) { $previousId = [string]$VoiceCombo.SelectedItem.Id }

    $items = New-Object 'System.Collections.ObjectModel.ObservableCollection[object]'
    try {
        $tokens = $script:Sapi.GetVoices('', '')
        for ($i = 0; $i -lt [int]$tokens.Count; $i++) {
            $token = $tokens.Item($i)
            $name = Get-TokenDescription $token
            $id = Get-TokenId $token
            $items.Add([pscustomobject]@{ Name = $name; Id = $id; Token = $token })
        }
    }
    catch {
        Show-AppError "Konuşma sesleri okunamadı.`r`n`r`n$($_.Exception.Message)"
    }

    $VoiceCombo.ItemsSource = $items
    $targetIndex = 0
    for ($i = 0; $i -lt $items.Count; $i++) {
        if ($previousId -and $items[$i].Id -eq $previousId) {
            $targetIndex = $i
            break
        }
        if (-not $previousId -and $items[$i].Name -match '(?i)Tolga|Emel|Turkish|Türk') {
            $targetIndex = $i
            break
        }
    }
    if ($items.Count -gt 0) {
        $VoiceCombo.SelectedIndex = $targetIndex
        $VoiceHint.Text = 'Yüklü Windows konuşma seslerinden biri seçilir.'
    }
    else {
        $VoiceHint.Text = 'Kullanılabilir konuşma sesi bulunamadı. Windows konuşma paketi eklemelisin.'
    }
}

function Save-Settings {
    try {
        if (-not (Test-Path $settingsDir)) {
            New-Item -ItemType Directory -Path $settingsDir -Force | Out-Null
        }
        $data = [ordered]@{
            DeviceId = if ($DeviceCombo.SelectedItem) { [string]$DeviceCombo.SelectedItem.Id } else { '' }
            VoiceId = if ($VoiceCombo.SelectedItem) { [string]$VoiceCombo.SelectedItem.Id } else { '' }
            Rate = [int]$RateSlider.Value
            Volume = [int]$VolumeSlider.Value
            AlwaysOnTop = [bool]$AlwaysOnTopCheck.IsChecked
        }
        $data | ConvertTo-Json | Set-Content -Path $settingsFile -Encoding UTF8
    }
    catch { }
}

function Restore-Settings {
    if (-not (Test-Path $settingsFile)) { return }
    try {
        $saved = Get-Content -Path $settingsFile -Raw | ConvertFrom-Json
        $RateSlider.Value = [int]$saved.Rate
        $VolumeSlider.Value = [int]$saved.Volume
        $AlwaysOnTopCheck.IsChecked = [bool]$saved.AlwaysOnTop

        for ($i = 0; $i -lt $DeviceCombo.Items.Count; $i++) {
            if ([string]$DeviceCombo.Items[$i].Id -eq [string]$saved.DeviceId) {
                $DeviceCombo.SelectedIndex = $i
                break
            }
        }
        for ($i = 0; $i -lt $VoiceCombo.Items.Count; $i++) {
            if ([string]$VoiceCombo.Items[$i].Id -eq [string]$saved.VoiceId) {
                $VoiceCombo.SelectedIndex = $i
                break
            }
        }
    }
    catch { }
}

function Set-Status {
    param([string]$Text, [string]$Color)
    $StatusText.Text = $Text
    $StatusDot.Fill = $Color
}

function Stop-Speaking {
    try {
        # SVSFPurgeBeforeSpeak = 2. Boş metinle mevcut ve bekleyen konuşmayı temizler.
        $null = $script:Sapi.Speak('', 2)
    }
    catch { }
    $script:IsSpeaking = $false
    Set-Status 'Durduruldu' '#E7A94B'
}

function Start-Speaking {
    $text = [string]$TextInput.Text
    if ([string]::IsNullOrWhiteSpace($text)) {
        [System.Windows.MessageBox]::Show('Önce okunacak bir metin yaz.', 'CaYa Virtual Voice', 'OK', 'Information') | Out-Null
        return
    }
    if (-not $DeviceCombo.SelectedItem) {
        [System.Windows.MessageBox]::Show('Bir ses çıkışı veya sanal kablo seç.', 'CaYa Virtual Voice', 'OK', 'Warning') | Out-Null
        return
    }
    if (-not $VoiceCombo.SelectedItem) {
        [System.Windows.MessageBox]::Show('Windows konuşma sesi bulunamadı.', 'CaYa Virtual Voice', 'OK', 'Warning') | Out-Null
        return
    }

    try {
        Stop-Speaking

        $script:Sapi.Rate = [int]$RateSlider.Value
        $script:Sapi.Volume = [int]$VolumeSlider.Value
        $script:Sapi.AllowAudioOutputFormatChangesOnNextSet = $true
        $script:Sapi.Voice = $VoiceCombo.SelectedItem.Token

        if ([string]$DeviceCombo.SelectedItem.Id -eq '__DEFAULT__') {
            $script:Sapi.AudioOutput = $null
        }
        else {
            $script:Sapi.AudioOutput = $DeviceCombo.SelectedItem.Token
        }

        Save-Settings
        Set-Status 'Konuşuyor…' '#4BA3FF'
        $script:IsSpeaking = $true

        # SVSFlagsAsync (1) + SVSFPurgeBeforeSpeak (2)
        $null = $script:Sapi.Speak($text, 3)
    }
    catch {
        $script:IsSpeaking = $false
        Set-Status 'Hata' '#FF6677'
        Show-AppError "Metin seslendirilemedi.`r`n`r`n$($_.Exception.Message)"
    }
}

Load-Devices
Load-Voices
Restore-Settings

$TextInput.Add_TextChanged({
    $CharCount.Text = "$($TextInput.Text.Length) karakter"
})
$CharCount.Text = "$($TextInput.Text.Length) karakter"

$RateSlider.Add_ValueChanged({ $RateValue.Text = [string][int]$RateSlider.Value })
$VolumeSlider.Add_ValueChanged({ $VolumeValue.Text = "$([int]$VolumeSlider.Value)%" })
$AlwaysOnTopCheck.Add_Checked({ $window.Topmost = $true; Save-Settings })
$AlwaysOnTopCheck.Add_Unchecked({ $window.Topmost = $false; Save-Settings })
$RefreshButton.Add_Click({ Load-Devices })
$SpeakButton.Add_Click({ Start-Speaking })
$StopButton.Add_Click({ Stop-Speaking })
$ClearButton.Add_Click({ $TextInput.Clear(); $TextInput.Focus() })
$SpeechSettingsButton.Add_Click({
    try { Start-Process 'ms-settings:speech' }
    catch { Start-Process 'control.exe' 'intl.cpl' }
})

$TextInput.Add_PreviewKeyDown({
    param($sender, $e)
    if ($e.Key -eq [System.Windows.Input.Key]::Enter -and
        ([System.Windows.Input.Keyboard]::Modifiers -band [System.Windows.Input.ModifierKeys]::Control)) {
        $e.Handled = $true
        Start-Speaking
    }
    elseif ($e.Key -eq [System.Windows.Input.Key]::Escape) {
        $e.Handled = $true
        Stop-Speaking
    }
})

$timer = New-Object System.Windows.Threading.DispatcherTimer
$timer.Interval = [TimeSpan]::FromMilliseconds(200)
$timer.Add_Tick({
    if ($script:IsSpeaking) {
        try {
            if ([bool]$script:Sapi.WaitUntilDone(0)) {
                $script:IsSpeaking = $false
                Set-Status 'Hazır' '#58C97A'
            }
        }
        catch {
            $script:IsSpeaking = $false
            Set-Status 'Hata' '#FF6677'
        }
    }
})
$timer.Start()

$window.Add_Closing({
    Save-Settings
    $timer.Stop()
    Stop-Speaking
    try { [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($script:Sapi) | Out-Null } catch { }
})

$window.Topmost = [bool]$AlwaysOnTopCheck.IsChecked
$TextInput.Focus()
$window.ShowDialog() | Out-Null
