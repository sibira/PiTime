#!/usr/bin/perl
##############################################################
#PiTime
#Version: 1.1 (26/02/2016)
#Copyright (c) 2015 Masahito Hayashi
#This software is released under the MIT Licenses:
#https://opensource.org/licenses/mit-license.php
##############################################################
#モジュール読み込み
use strict;
use warnings;
use Encode;
use JSON;
use Time::Local;
use CGI qw(:standard);
use Calendar::Japanese::Holiday;
#################################################################################
#ここから変更可能
#################################################################################
#パラメータ変更用

#天気:エリア番号
my $weather_area = 130010;

#無線インターフェース(wlan* or eth*)
my $para_interface = "wlan0";

#再生デイバス番号(番号 or none)
my $para_int_vol1 = "0";

#録音デイバス番号(番号 or none)
my $para_int_vol2 = "none";

#閾値
my $threshold_net = 50;	#ネットワーク品質下限(%)
my $threshold_df = 75;	#ディスク使用率上限(%)
my $threshold_mem = 75;	#メモリ使用率上限(%)
my $threshold_la = 0.75;	#ロードアベレージ上限
my $threshold_volt1 = 1.05;	#電圧下限(Volt)
my $threshold_volt2 = 1.35;	#電圧上限(Volt)
my $threshold_tmp = 60;	#温度上限('C)

#ページリロード(デフォルト:3600000/1時間)
my $page_reload = 3600000;

#################################################################################
#デザイン変更用

#デザイン変更:横幅(px)
my $display_width = 800;

#デザイン変更:縦幅(px)
my $display_height = 480;

#デザイン変更:システム部フォントサイズ
my $font_system = 16;

#デザイン変更:日付部フォントサイズ
my $font_day = 50;

#デザイン変更:時間部フォントサイズ
my $font_main = 160;

#デザイン変更:天気部フォントサイズ
my $font_table = 25;

#デザイン変更:フォント
my $font_family = "Roboto";

#デザイン変更:背景色
my $html_style_back = "000000";

#デザイン変更:文字色
my $html_style_color1 = "FF8800";
my $html_style_color2 = "DDDDDD";
my $html_style_color3 = "FFFFFF";

#デザイン変更:サークル背景色
my $html_circle_bcolor1_1 = "888888";
my $html_circle_bcolor1_2 = "666666";
my $html_circle_bcolor1_3 = "444444";
my $html_circle_bcolor2 = "333333";
my $html_circle_bcolor_error = "880000";

#デザイン変更:サークル色/時間
my $html_circle_color1_1 = "0044FF";
my $html_circle_color1_2 = "0022FF";
my $html_circle_color1_3 = "0000FF";
my $html_circle_color1_str = "0044FF";

#デザイン変更:サークル色/Network
my $html_circle_color2_1 = "88FFAA";
my $html_circle_color2_2 = "88FF88";
my $html_circle_color2_3 = "88FF66";
my $html_circle_color2_str = "88FFAA";

#デザイン変更:サークル色/System
my $html_circle_color3_1 = "AAAAFF";
my $html_circle_color3_2 = "AA88FF";
my $html_circle_color3_3 = "AA66FF";
my $html_circle_color3_4 = "AA55FF";
my $html_circle_color3_5 = "AA44FF";
my $html_circle_color3_str = "AAAAFF";

#デザイン変更:サークル色/vol
my $html_circle_color4 = "FFFF00";

#デザイン変更:サークル色/その他
my $html_circle_color5 = "DDDDDD";
my $html_circle_error = "FF0000";

#デザイン変更:Message色
my $html_msg_color1 = "0000CC";
my $html_msg_color2 = "CC0000";

#デザイン変更:カレンダー色
my $html_calendar_today = "DDDDDD";
my $html_calendar_saturday_b = "2222AA";
my $html_calendar_sunday_b = "AA2222";
my $html_calendar_holiday = "22AA22";
my $html_calendar_saturday_s = "3333FF";
my $html_calendar_sunday_s = "FF3333";

#デザイン変更:コマンド文字色
my $html_command = "00FF88";

#デザイン変更:天気文字色
my $weather_color1 = "FFFFFF";
my $weather_color2 = "FF3333";

#################################################################################

#dmesg内でエラーと判断するもの
my @error_word;
$error_word[$#error_word+1] = 'error';
$error_word[$#error_word+1] = 'warning';
$error_word[$#error_word+1] = 'fail';
$error_word[$#error_word+1] = 'Can\'t/';
$error_word[$#error_word+1] = 'I\/O';
#$error_word[$#error_word+1] = '●●●';	#add word

#エラーと判断した行で以下文字が入っていた場合除外
my @exc_word;
$exc_word[$#exc_word+1] = 'flexfb';
#$exc_word[$#exc_word+1] = '●●●';	#add word

#################################################################################
#ここまで変更可能
#################################################################################

#再起動/停止
my $post_data = param('system');	#postデータ代入
my $post_access = param('access');	#postデータ代入
my $midori_ps = `ps ax | grep /usr/bin/midori | head -n 1 | cut -d " " -f 2`;
if ( $post_data and $post_access and $post_data eq "bclose" and $post_access eq "127.0.0.1" ) {
	system ("kill $midori_ps");
	exit;
} elsif ( $post_data and $post_access and $post_data eq "reboot" and $post_access eq "127.0.0.1" ) {
	print "Content-Type: text/html; charset=UTF-8\n\n";
	print "<!DOCTYPE html>\n";
	print "<html>reboot now</html>\n";
	system ("sudo reboot");
	exit;
} elsif ( $post_data and $post_access and $post_data eq "poweroff" and $post_access eq "127.0.0.1" ) {
	print "Content-Type: text/html; charset=UTF-8\n\n";
	print "<!DOCTYPE html>\n";
	print "<html>poweroff now</html>\n";
	system ("sudo poweroff");
	exit;
}
#################################################################################

#ネットワーク疎通と天気取得
my $para_ping = `ping -c 1 8.8.8.8 | grep " 0% packet loss"`;
my ($weather_data01,$weather_data02,$weather_data03,$weather_data01_day,$weather_data02_day,$weather_data03_day,$weather_data_city);
my ($weather_data01_tmp_max,$weather_data01_tmp_min,$weather_data02_tmp_max,$weather_data02_tmp_min,$weather_data03_tmp_max,$weather_data03_tmp_min);

if ( $para_ping ) {
	my $json = decode_json(`curl -s http://weather.livedoor.com/forecast/webservice/json/v1?city=$weather_area`);
	$weather_data01 = &weather_text(encode("utf-8",$json->{forecasts}->[0]->{telop}));
	$weather_data02 = &weather_text(encode("utf-8",$json->{forecasts}->[1]->{telop}));
	$weather_data03 = &weather_text(encode("utf-8",$json->{forecasts}->[2]->{telop}));
	$weather_data01_day = &weather_date($json->{forecasts}->[0]->{date});
	$weather_data02_day = &weather_date($json->{forecasts}->[1]->{date});
	$weather_data03_day = &weather_date($json->{forecasts}->[2]->{date});
	$weather_data01_tmp_max = $json->{forecasts}->[0]->{temperature}->{max}->{celsius};
	$weather_data01_tmp_min = $json->{forecasts}->[0]->{temperature}->{min}->{celsius};
	$weather_data02_tmp_max = $json->{forecasts}->[1]->{temperature}->{max}->{celsius};
	$weather_data02_tmp_min = $json->{forecasts}->[1]->{temperature}->{min}->{celsius};
	$weather_data03_tmp_max = $json->{forecasts}->[2]->{temperature}->{max}->{celsius};
	$weather_data03_tmp_min = $json->{forecasts}->[2]->{temperature}->{min}->{celsius};
	$weather_data_city  = encode("utf-8",$json->{location}->{city});
}

#システム値取得
my $para_tmp = `/opt/vc/bin/vcgencmd measure_temp | cut -d "=" -f 2 | sed -e "s/\'C//"`;
my $para_volt = sprintf("%.2f",`/opt/vc/bin/vcgencmd measure_volts core | cut -d "=" -f 2 | sed -e "s/V//"`);
my $para_la = `uptime |sed -e "s/ //g" | cut -d "," -f 5`;
my $para_df = `df | grep /dev/root | sed -e "s/  */ /g" | cut -d " " -f 5 | sed -e "s/\%//"`;
my $para_mem1 = `cat /proc/meminfo | grep MemTotal: | sed -e "s/  */ /g" | cut -d " " -f 2`;
my $para_mem2 = `cat /proc/meminfo | grep MemAvailable: | sed -e "s/  */ /g" | cut -d " " -f 2`;
$para_tmp =~ s/\n//g;
$para_la =~ s/\n//g;
$para_df =~ s/\n//g;
$para_mem1 =~ s/\n//g;
$para_mem2 =~ s/\n//g;
my $para_mem3 = sprintf("%d",((($para_mem1-$para_mem2)/$para_mem1)*100));
my @para_dmesg = `dmesg`;
my $para_errormsg;
my $exc_check = 0;
foreach my $value1 (@para_dmesg) {
	foreach my $value2 (@error_word) {
		if ( "$value1" =~ /$value2/ ) {
			foreach my $value3 (@exc_word) {
				if ( "$value1" =~ /$value3/ ) {
					$exc_check = 1;
				}
				if ( $exc_check == 0 ) {
					$para_errormsg .= $value1." ";
				}
			}
		}
	}
}
if ( $para_errormsg ) { $para_errormsg = substr($para_errormsg,0,175); $html_circle_color5 = $html_circle_error; }
#ボリューム取得
my $para_vol1 = 0;
my $para_vol2 = 0;
if ( $para_int_vol1 ne "none" ) { $para_vol1 = `/usr/bin/amixer -c $para_int_vol1 | grep % | cut -d " " -f 6 | sed -e "s/\%//g" | sed -e "s/\\[//g" | sed -e "s/\\]//g"`; }
if ( $para_int_vol2 ne "none" ) { $para_vol2 = `/usr/bin/amixer -c $para_int_vol2 | grep % | cut -d " " -f 6 | sed -e "s/\%//g" | sed -e "s/\\[//g" | sed -e "s/\\]//g"`; }
#ネットワーク取得
my ($para_net1,$para_net2,$para_net3);
my (@para_net_tmp1,@para_net_tmp2);
if ( "$para_interface" =~ /wlan/ ) {
	my $para_net_c = `/sbin/iwconfig $para_interface | grep "Link Quality" | sed -e "s/  */ /g"`;
	if ( $para_net_c ) {
		@para_net_tmp1 = split (/Noise level=/,$para_net_c);
		@para_net_tmp2 = split (/\//,$para_net_tmp1[1]);
		$para_net1 = 100-$para_net_tmp2[0];
		@para_net_tmp1 = split (/Signal level=/,$para_net_c);
		@para_net_tmp2 = split (/\//,$para_net_tmp1[1]);
		$para_net2 = $para_net_tmp2[0];
		@para_net_tmp1 = split (/Link Quality=/,$para_net_c);
		@para_net_tmp2 = split (/\//,$para_net_tmp1[1]);
		$para_net3 = $para_net_tmp2[0];
	}
} elsif ( "$para_interface" =~ /eth/ ) {
		$para_net1 = `/sbin/ethtool $para_interface 2> /dev/null | grep 'Link detected:' | sed -e "s/ //g"`;
		$para_net2 = `/sbin/ethtool $para_interface 2> /dev/null | grep 'Speed:' | sed -e "s/ //g" | sed -e "s/Mb\\/s//g"`;
		$para_net3 = `/sbin/ethtool $para_interface 2> /dev/null | grep 'Duplex:' | sed -e "s/ //g"`;
		$para_net1 =~ s/\n//g;
		$para_net2 =~ s/\n//g;
		$para_net3 =~ s/\n//g;
		@para_net_tmp1 = split (/:/,$para_net1);
		$para_net1 = $para_net_tmp1[1];
		@para_net_tmp1 = split (/:/,$para_net2);
		$para_net2 = $para_net_tmp1[1];
		@para_net_tmp1 = split (/:/,$para_net3);
		$para_net3 = $para_net_tmp1[1];
		if ( $para_net1 eq "yes" ) { $para_net1 = 100; } else { $para_net1 = 0; }
		if ( $para_net3 eq "Full" ) { $para_net3 = 100; } else { $para_net3 = 0; }
}

#値確認
#net1
if ( $para_net1 and  $para_net1 !~ /^[0-9.]*$/ ) {
	$para_net1 = 0;
}
if ( $para_net1 and $para_net1 < $threshold_net ) {
	$html_circle_color2_1 = $html_circle_error;
	$html_circle_color2_str = $html_circle_error;
	$html_circle_color5 = $html_circle_error;
	$html_circle_bcolor2 = $html_circle_bcolor_error;
}
#net2
if ( $para_net2 and $para_net2 !~ /^[0-9.]*$/ ) {
	$para_net2 = 0;
}
if ( $para_net2 and $para_net2 < $threshold_net ) {
	$html_circle_color2_2 = $html_circle_error;
	$html_circle_color2_str = $html_circle_error;
	$html_circle_color5 = $html_circle_error;
	$html_circle_bcolor2 = $html_circle_bcolor_error;
}
#net3
if ( $para_net3 and $para_net3 !~ /^[0-9.]*$/ ) {
	$para_net3 = 0;
}
if ( $para_net3 and $para_net3 < $threshold_net ) {
	$html_circle_color2_3 = $html_circle_error;
	$html_circle_color2_str = $html_circle_error;
	$html_circle_color5 = $html_circle_error;
	$html_circle_bcolor2 = $html_circle_bcolor_error;
}
#df
if ( $para_df !~ /^[0-9.]*$/ ) {
	$para_df = 0;
}
if ( $para_df > $threshold_df ) {
	$html_circle_color3_1 = $html_circle_error;
	$html_circle_color3_str = $html_circle_error;
	$html_circle_color5 = $html_circle_error;
	$html_circle_bcolor2 = $html_circle_bcolor_error;
}
#mem
if ( $para_mem3 !~ /^[0-9.]*$/ ) {
	$para_mem3 = 0;
}
if ( $para_mem3 > $threshold_mem ) {
	$html_circle_color3_2 = $html_circle_error;
	$html_circle_color3_str = $html_circle_error;
	$html_circle_color5 = $html_circle_error;
	$html_circle_bcolor2 = $html_circle_bcolor_error;
}
#la
if ( $para_la !~ /^[0-9.]*$/ ) {
	$para_la = 0;
}
if ( $para_la > $threshold_la ) {
	$html_circle_color3_3 = $html_circle_error;
	$html_circle_color3_str = $html_circle_error;
	$html_circle_color5 = $html_circle_error;
	$html_circle_bcolor2 = $html_circle_bcolor_error;
}
#volt
if ( $para_volt !~ /^[0-9.]*$/ ) {
	$para_volt = 0;
}
if ( $threshold_volt1 > $para_volt or $para_volt > $threshold_volt2 ) {
	$html_circle_color3_4 = $html_circle_error;
	$html_circle_color3_str = $html_circle_error;
	$html_circle_color5 = $html_circle_error;
	$html_circle_bcolor2 = $html_circle_bcolor_error;
}
#tmp
if ( $para_tmp !~ /^[0-9.]*$/ ) {
	$para_tmp = 0;
}
if ( $para_tmp > $threshold_tmp ) {
	$html_circle_color3_5 = $html_circle_error;
	$html_circle_color3_str = $html_circle_error;
	$html_circle_color5 = $html_circle_error;
	$html_circle_bcolor2 = $html_circle_bcolor_error;
}
#vol1
if ( $para_vol1 !~ /^[0-9.]*$/ ) {
	$para_vol1 = 0;
}
#vol2
if ( $para_vol2 !~ /^[0-9.]*$/ ) {
	$para_vol2 = 0;
}

#HTML開始
print "Content-Type: text/html; charset=UTF-8\n\n";
print "<!DOCTYPE html>\n";
print "<html>\n";
print "<head>\n";
print "<meta charset=\"UTF-8\">\n";
print "<title>TIME</title>\n";

#Java
print "<script type=\"text/javascript\" src=\"../js/jquery-2.1.4.min.js\"></script>\n";
print "<script type=\"text/javascript\" src=\"../js/jquery.knob-1.2.12.js\"></script>\n";
print "<script>\$(function(){ \$(\".knob\").knob(); });</script>\n";

#スタイルシート開始
print "<style type=\"text/css\">\n";
print "<!--\n";
print "* {\n";
print "padding:0px;\n";
print "margin:0px;\n";
print "}\n";

#body用
print "body {\n";
print "background-color:#".$html_style_back.";\n";
print "text-align:center;\n";
print "font-family:".$font_family.";\n";
print "font-weight:bold;\n";
print "}\n";

#aリンク
print "a {\n";
print "display:block;width:100%;height:100%;\n";
print "}\n";

#div用system
print ".time_system{\n";
print "width:".$display_width."px;\n";
print "height:".($display_height*0.05)."px;\n";
print "font-size:".$font_system."px;\n";
print "color:#".$html_style_color1.";\n";
print "background-color:#".$html_style_back.";\n";
print "}\n";

#div用main
print ".time_main{\n";
print "width:".$display_width."px;\n";
print "height:".($display_height*0.55)."px;\n";
print "}\n";

#div用main-circle
print ".time_circle{\n";
print "width:".($display_width*0.4)."px;\n";
print "height:".($display_height*0.55)."px;\n";
print "background-color:#".$html_style_back.";\n";
print "float:left;\n";
print "}\n";

#div用main-day
print ".time_day{\n";
print "height:".($display_height*0.15)."px;\n";
print "font-size:".$font_day."px;\n";
print "color:#".$html_style_color3.";\n";
print "background-color:#".$html_style_back.";\n";
print "}\n";

#div用main-time
print ".time_time{\n";
print "height:".($display_height*0.4)."px;\n";
print "font-size:".$font_main."px;\n";
print "line-height:".($display_height*0.35)."px;\n";
print "color:#".$html_style_color3.";\n";
print "background-color:#".$html_style_back.";\n";
print "}\n";

#div用message
print ".time_message{\n";
print "width:".$display_width."px;\n";
print "height:".($display_height*0.1)."px;\n";
print "font-size:".$font_system."px;\n";
print "text-align:left;\n";
print "color:#".$html_style_color1.";\n";
print "background-color:#".$html_style_back.";\n";
print "}\n";

#div用weather
print ".time_weather{\n";
print "width:".$display_width."px;\n";
print "height:".($display_height*0.3)."px;\n";
print "}\n";

#table用
print ".tablestyle {\n";
print "border-collapse: collapse;\n";
print "width:".$display_width."px;\n";
print "height:".($display_height*0.3)."px;\n";
print "}\n";
print ".tablestyle td {\n";
print "border:1px solid #".$html_style_color2.";\n";
print "background-color:#".$html_style_back.";\n";
print "color:#".$html_style_color1.";\n";
print "font-size:".$font_table."px;\n";
print "}\n";

#カレンダーtable用
print ".table_calendar {\n";
print "border-collapse: collapse;\n";
print "width:100%;\n";
print "height:100%;\n";
print "}\n";
print ".table_calendar td {\n";
print "border:1px solid #".$html_style_color2.";\n";
print "background-color:#".$html_style_back.";\n";
print "color:#".$html_style_color1.";\n";
print "font-size:14px;\n";
print "}\n";

#スタイルシート終了
print "-->\n";
print "</style>\n";
print "</head>\n";
print "<body>\n";

#System表示
print "<div class=\"time_system\">\n";
if ( $para_tmp ) { 	print "[TMP:<span style=\"color:#".$html_circle_color3_5.";\">".$para_tmp."</span>'C] \n"; }
if ( $para_volt ) { print "[VOLT:<span style=\"color:#".$html_circle_color3_4.";\">".$para_volt."</span>V] \n"; }
if ( $para_la ) { print "[LOAD:<span style=\"color:#".$html_circle_color3_3.";\">".$para_la."</span>] \n"; }
if ( $para_mem3 ) { print "[MEM:<span style=\"color:#".$html_circle_color3_2.";\">".$para_mem3."</span>%] \n"; }
if ( $para_df ) { print "[DISK:<span style=\"color:#".$html_circle_color3_1.";\">".$para_df."</span>%] \n"; }
if ( "$para_interface" =~ /wlan/ ) {
	if ( $para_net3 ) { print "[Quality:<span style=\"color:#".$html_circle_color2_3.";\">".$para_net3."</span>%] \n"; }
	if ( $para_net2 ) { print "[Signal:<span style=\"color:#".$html_circle_color2_2.";\">".$para_net2."</span>%] \n"; }
	if ( $para_net1 ) { print "[Clear:<span style=\"color:#".$html_circle_color2_1.";\">".$para_net1."</span>%]\n"; }
} elsif ( "$para_interface" =~ /eth/ ) {
	if ( $para_net3 ) { print "[Link:<span style=\"color:#".$html_circle_color2_3.";\">".$para_net3."</span>] \n"; }
	if ( $para_net2 ) { print "[Speed:<span style=\"color:#".$html_circle_color2_2.";\">".$para_net2."</span>] \n"; }
	if ( $para_net1 ) { print "[Duplex:<span style=\"color:#".$html_circle_color2_1.";\">".$para_net1."</span>]\n"; }
}
print "</div>\n";

#Message表示
print "<div class=\"time_message\">\n";
print "Message:\n";
if ( $para_errormsg ) {
	print "<span style=\"color:#".$html_msg_color2.";\">".$para_errormsg."</span>\n";
} else {
	print "<span style=\"color:#".$html_msg_color1.";\">No Message</span>\n";
}
print "</div>\n";

#メイン表示
print "<div class=\"time_main\">\n";
print "<div class=\"time_circle\">\n"; &write_circle(); print "</div>\n";
print "<div class=\"time_day\"><p id=\"ClockData1\"> / ( )</p></div>\n";
print "<div class=\"time_time\"><p id=\"ClockData2\">:</p></div>\n";
print "</div>\n";

#テーブル表示
print "<div class=\"time_weather\">\n";
print "<table class=\"tablestyle\">\n";
#天気:日付
print "<tr style=\"height:".($display_height*0.075)."px;\">\n";
print "<td style=\"width:".($display_width*0.175)."px;\">DATE</td>\n";
print "<td style=\"width:".($display_width*0.175)."px;\">";
if ( $weather_data01_day ) { print $weather_data01_day; } else { print "___"; }
print "</td>\n";
print "<td style=\"width:".($display_width*0.175)."px;\">";
if ( $weather_data02_day ) { print $weather_data02_day; } else { print "___"; }
print "</td>\n";
print "<td style=\"width:".($display_width*0.175)."px;\">";
if ( $weather_data03_day ) { print $weather_data03_day; } else { print "___"; }
print "</td>\n";

#カレンダー部分
print "<td style=\"width:".($display_width*0.3)."px;\" rowspan=\"4\">\n";
my ($nowday,$nowmon,$nowyear) = (localtime(time))[3..5];
my $starttime = timelocal(0,0,0,1,$nowmon,$nowyear);
my $swday = (localtime($starttime))[6];
print "<table class=\"table_calendar\" cols=7 border=0>\n";
print "<tr><td><span style=\"color:#".$html_calendar_sunday_s.";\">S</span></td><td>M</td><td>T</td><td>W</td><td>T</td><td>F</td><td><span style=\"color:#".$html_calendar_saturday_s.";\">S</span></td></tr>\n";
foreach my $week (0 .. 5) {
	my $sunday = $starttime - $swday * 86400 + $week * 7 * 86400;
	my $sunmon = (localtime($sunday))[4];
	last if ($week == 5 and $sunmon != $nowmon and $week >= 0);
	print "<tr>\n";
	foreach my $day (0 .. 6){
		my $today = $starttime + ($day - $swday + $week * 7) * 86400;
		my ($mday,$mon,$year,$wday) = (localtime($today))[3..6];
		if ( $mon == $nowmon and $nowday == $mday ) {
			print "<td style=\"background-color:#".$html_calendar_today.";\">";
		} elsif ( $mday and $mon == $nowmon and $wday == 0 ) {
			print "<td style=\"background-color:#".$html_calendar_sunday_b.";\">";
		} elsif ( $mday and $mon == $nowmon and $wday == 6 ) {
			print "<td style=\"background-color:#".$html_calendar_saturday_b.";\">";
		} elsif ( $mday and $mon == $nowmon and isHoliday($nowyear+1900,$nowmon+1,$mday,1) ) {
			print "<td style=\"background-color:#".$html_calendar_holiday.";\">";
		} else {
			print "<td>";
		}
		if ( $week == 0 and $day >= $swday or $week > 0) {
			if ($mon == $nowmon) {
				print $mday;
			}
		}
		print "</td>\n";
	}
	print "</tr>\n";
}
print "</table>";
print "</td>\n";
print "</tr>\n";

#天気:データ
print "<tr style=\"height:".($display_height*0.075)."px;\">\n";
print "<td style=\"color:#".$weather_color2.";\">";
if ( $weather_data_city ) { print "$weather_data_city\n"; } else { print "___\n"; }
print "</td>\n";
print "<td style=\"color:#".$weather_color1.";\">";
if ( $weather_data01 ) { print "$weather_data01\n"; } else { print "___\n"; }
print "</td>\n";
print "<td style=\"color:#".$weather_color1.";\">";
if ( $weather_data02 ) { print "$weather_data02\n"; } else { print "___\n"; }
print "</td>\n";
print "<td style=\"color:#".$weather_color1.";\">";
if ( $weather_data03 ) { print "$weather_data03\n"; } else { print "___\n"; }
print "</td>\n";
print "</tr>\n";

#温度
print "<tr style=\"height:".($display_height*0.075)."px;\">\n";
print "<td>Max/Min</td>\n";
print "<td style=\"color:#".$weather_color1.";\">\n";
if ( $weather_data01_tmp_max or $weather_data01_tmp_min ) {
	if ( $weather_data01_tmp_max ) { print "$weather_data01_tmp_max～" } else { print "_～"; }
	if ( $weather_data01_tmp_min ) { print "$weather_data01_tmp_min\n" } else { print "_"; }
}
print "</td>\n";
print "<td style=\"color:#".$weather_color1.";\">\n";
if ( $weather_data02_tmp_max or $weather_data02_tmp_min ) {
	if ( $weather_data02_tmp_max ) { print "$weather_data02_tmp_max～" } else { print "_～"; }
	if ( $weather_data02_tmp_min ) { print "$weather_data02_tmp_min\n" } else { print "_"; }
}
print "</td>\n";
print "<td style=\"color:#".$weather_color1.";\">\n";
if ( $weather_data03_tmp_max or $weather_data03_tmp_min ) {
	if ( $weather_data03_tmp_max ) { print "$weather_data03_tmp_max～" } else { print "_～"; }
	if ( $weather_data03_tmp_min ) { print "$weather_data03_tmp_min\n" } else { print "_"; }
}
print "</td>\n";
print "</tr>\n";

#アイコン
print "<tr>\n";
print "<td style=\"cursor:pointer;\" onclick=\"page_jump1()\"><span style=\"color:#".$html_command.";\">[Reload]</span></td>\n";
print "<td style=\"cursor:pointer;\" onclick=\"page_jump2()\"><span style=\"color:#".$html_command.";\">[BClose]</span></td>\n";
print "<td style=\"cursor:pointer;\" onclick=\"page_jump3()\"><span style=\"color:#".$html_command.";\">[Reboot]</span></td>\n";
print "<td style=\"cursor:pointer;\" onclick=\"page_jump4()\"><span style=\"color:#".$html_command.";\">[Pw-off]</span></td>\n";
print "</tr>\n";
#テーブル終了
print "</table>\n";
print "</div>\n";

#Java
print "<script type=\"text/javascript\">\n";
#日時表示
print "function clockprint() {\n";
print "var nowTime = new Date();\n";
print "var nowDate = nowTime.getDate();\n";
print "var nowMonth = nowTime.getMonth() + 1;\n";
print "nowDay = nowTime.getDay();\n";
print "var nowWeek = new Array(\"日\",\"月\",\"火\",\"水\",\"木\",\"金\",\"土\");\n";
print "var nowHour = timeedit( nowTime.getHours() );\n";
print "var nowMin = timeedit( nowTime.getMinutes() );\n";
print "var msg1 = nowMonth + \" / \" + nowDate + \" (\" + nowWeek[nowDay] + \")\";\n";
print "var msg2 = nowHour + \":\" + nowMin;\n";
print "document.getElementById(\"ClockData1\").innerHTML = msg1;\n";
print "document.getElementById(\"ClockData2\").innerHTML = msg2;\n";
print "}\n";
print "setInterval('clockprint()',1000);\n";
print "clockprint();\n";
#日時表示サブ
print "function timeedit(num) {\n";
print "var ret;\n";
print "if( num < 10 ) { ret = \"0\" + num; }\n";
print "else { ret = num; }\n";
print "return ret;\n";
print "}\n";
#ページリロード用
print "function pagereload() {\n";
print "location.reload();\n";
print "}\n";
print "setInterval('pagereload()',600000);\n";
#ボタン用
print "function page_jump1(){\n";
print "location.href = \"./time.cgi\";\n";
print "}\n";
print "function page_jump2(){\n";
print "if (confirm(\"ブラウザを終了しますか？\")==true)\n";
print "location.href = \"./time.cgi?system=bclose&access=$ENV{'REMOTE_ADDR'}\";\n";
print "}\n";
print "function page_jump3(){\n";
print "if (confirm(\"再起動しますか？\")==true)\n";
print "location.href = \"./time.cgi?system=reboot&access=$ENV{'REMOTE_ADDR'}\";\n";
print "}\n";
print "function page_jump4(){\n";
print "if (confirm(\"シャットダウンしますか？\")==true)\n";
print "location.href = \"./time.cgi?system=poweroff&access=$ENV{'REMOTE_ADDR'}\";\n";
print "}\n";
print "</script>\n";

#HTML終了
print "</body>\n";
print "</html>\n";

#CGI終了
exit;

#サブルーチン
sub weather_date {
	if ( $_[0] ) {
		my $data = $_[0];
		$data =~ s/\'//g;
		my @split_data = split (/\-/,$data);
		$data = "$split_data[1]\/$split_data[2]";
		return ($data);
	}
}

sub weather_text {
	if ( $_[0] ) {
		my $data = $_[0];
		$data =~ s/晴/<span style=\"color:#33FF33;\">晴<\/span>/g;
		$data =~ s/雨/<span style=\"color:#3333FF;\">雨<\/span>/g;
		$data =~ s/曇/<span style=\"color:#FF33AA;\">曇<\/span>/g;
		$data =~ s/雪/<span style=\"color:#AAAAFF;\">雪<\/span>/g;
		return ($data);
	}
}

sub write_circle {
	my ($now_sec,$now_min,$now_hour) = (localtime(time))[0..2];
	print "<script>\n";
	print "function clock() {\n";
	print "var \$s = \$(\".second\"),\n";
	print "\$m = \$(\".minute\"),\n";
	print "\$h = \$(\".hour\");\n";
	print "d = new Date(),\n";
	print "s = d.getSeconds(),\n";
	print "m = d.getMinutes(),\n";
	print "h = d.getHours();\n";
	print "\$s.val(s).trigger(\"change\");\n";
	print "\$m.val(m).trigger(\"change\");\n";
	print "\$h.val(h).trigger(\"change\");\n";
	print "setTimeout(\"clock()\",1000);\n";
	print "}\n";
	print "clock();\n";
	print "</script>\n";
	print "<div style=\"position:relative;width:".($display_width*0.375)."px;height:250;margin:auto;\">\n";
	#文字:TIME
	print "<div style=\"position:absolute;left:160px;top:0px;\">\n";
	print "<span style=\"color:#".$html_circle_color1_str.";text-decoration:underline;\">　　　time</span>\n";
	print "</div>\n";
	#文字:NetworkInterface
	print "<div style=\"position:absolute;left:200px;top:30px;\">\n";
	print "<span style=\"color:#".$html_circle_color2_str.";text-decoration:underline;\">　　$para_interface</span>\n";
	print "</div>\n";
	#文字:システム
	print "<div style=\"position:absolute;left:225px;top:60px;\">\n";
	print "<span style=\"color:#".$html_circle_color3_str.";text-decoration:underline;\">　　sys</span>\n";
	print "</div>\n";
	#文字:VOL
	print "<div style=\"position:absolute;left:0px;top:25px;\">\n";
	print "<span style=\"color:#".$html_circle_color4.";text-decoration:underline;\">vol　　</span>\n";
	print "</div>\n";
	#文字:オンライン/オフライン
	print "<div style=\"position:absolute;left:180px;top:220px;\">\n";
	if ( $para_ping ) {
		print "<span style=\"color:#".$html_circle_color2_str.";text-decoration:underline;\">　　OnLine</span>\n";
	} else {
		print "<span style=\"color:#".$html_circle_error.";text-decoration:underline;\">　　OffLine</span>\n";
	}
	print "</div>\n";
	#文字:Normal/Error
	print "<div style=\"position:absolute;left:0px;top:235px;\">\n";
	if ( $html_circle_color5 ne $html_circle_error ) {
		print "<span style=\"color:#".$html_circle_color5.";text-decoration:underline;\">Normal</span>\n";
	} else {
		print "<span style=\"color:#".$html_circle_color5.";text-decoration:underline;\">Error</span>\n";
	}
	print "</div>\n";
	#sec
	print "<div style=\"position:absolute;left:0px;top:0px;\">\n";
	print "<input \n";
	print "class=\"knob second\"\n";
	print "value=\"$now_sec\"\n";
	print "data-angleOffset=\"0\"\n";
	print "data-min=\"0\"\n";
	print "data-max=\"60\"\n";
	print "data-bgColor=\"#".$html_circle_bcolor1_1."\"\n";
	print "data-fgColor=\"#".$html_circle_color1_1."\"\n";
	print "data-displayInput=false\n";
	print "data-width=\"250\"\n";
	print "data-height=\"250\"\n";
	print "data-thickness=\".1\"\n";
	print "data-cursor=true\n";
	print ">\n";
	print "</div>\n";
	#min
	print "<div style=\"position:absolute;left:10px;top:10px;\">\n";
	print "<input \n";
	print "class=\"knob minute\"\n";
	print "value=\"$now_min\"\n";
	print "data-angleOffset=\"270\"\n";
	print "data-min=\"0\"\n";
	print "data-max=\"60\"\n";
	print "data-bgColor=\"#".$html_circle_bcolor1_2."\"\n";
	print "data-fgColor=\"#".$html_circle_color1_2."\"\n";
	print "data-displayInput=false\n";
	print "data-width=\"230\"\n";
	print "data-height=\"230\"\n";
	print "data-thickness=\".12\"\n";
	print ">\n";
	print "</div>\n";
	#hour
	print "<div style=\"position:absolute;left:20px;top:20px;\">\n";
	print "<input \n";
	print "class=\"knob hour\"\n";
	print "value=\"$now_hour\"\n";
	print "data-angleOffset=\"0\"\n";
	print "data-min=\"0\"\n";
	print "data-max=\"24\"\n";
	print "data-bgColor=\"#".$html_circle_bcolor1_3."\"\n";
	print "data-fgColor=\"#".$html_circle_color1_3."\"\n";
	print "data-displayInput=false\n";
	print "data-width=\"210\"\n";
	print "data-height=\"210\"\n";
	print "data-thickness=\".14\"\n";
	print ">\n";
	print "</div>\n";
	#net1
	print "<div style=\"position:absolute;left:30px;top:30px;\">\n";
	print "<input \n";
	print "class=\"knob\"\n";
	print "data-angleOffset=\"120\"\n";
	print "data-bgColor=\"#".$html_circle_bcolor2."\"\n";
	print "data-fgColor=\"#".$html_circle_color2_1."\"\n";
	print "data-width=\"190\"\n";
	print "data-readOnly=true\n";
	if ( $para_net1 ) { print "value=\"$para_net1\"\n"; }
	print "data-min=\"0\"\n";
	print "data-max=\"100\"\n";
	print "data-displayInput=false\n";
	print "data-thickness=\".05\"\n";
	print ">\n";
	print "</div>\n";
	#net2
	print "<div style=\"position:absolute;left:35px;top:35px;\">\n";
	print "<input \n";
	print "class=\"knob\"\n";
	print "data-angleOffset=\"240\"\n";
	print "data-bgColor=\"#".$html_circle_bcolor2."\"\n";
	print "data-fgColor=\"#".$html_circle_color2_2."\"\n";
	print "data-width=\"180\"\n";
	print "data-readOnly=true\n";
	if ( $para_net2 ) { print "value=\"$para_net2\"\n"; }
	print "data-min=\"0\"\n";
	print "data-max=\"100\"\n";
	print "data-displayInput=false\n";
	print "data-thickness=\".055\"\n";
	print ">\n";
	print "</div>\n";
	#net3
	print "<div style=\"position:absolute;left:40px;top:40px;\">\n";
	print "<input \n";
	print "class=\"knob\"\n";
	print "data-angleOffset=\"0\"\n";
	print "data-bgColor=\"#".$html_circle_bcolor2."\"\n";
	print "data-fgColor=\"#".$html_circle_color2_3."\"\n";
	print "data-width=\"170\"\n";
	print "data-readOnly=true\n";
	if ( $para_net3 ) { print "value=\"$para_net3\"\n"; }
	print "data-min=\"0\"\n";
	print "data-max=\"100\"\n";
	print "data-displayInput=false\n";
	print "data-thickness=\".06\"\n";
	print ">\n";
	print "</div>\n";
	#df
	print "<div style=\"position:absolute;left:45px;top:45px;\">\n";
	print "<input \n";
	print "class=\"knob\"\n";
	print "data-angleOffset=\"72\"\n";
	print "data-bgColor=\"#".$html_circle_bcolor2."\"\n";
	print "data-fgColor=\"#".$html_circle_color3_1."\"\n";
	print "data-width=\"160\"\n";
	print "data-readOnly=true\n";
	print "value=\"$para_df\"\n";
	print "data-min=\"0\"\n";
	print "data-max=\"100\"\n";
	print "data-displayInput=false\n";
	print "data-thickness=\".065\"\n";
	print ">\n";
	print "</div>\n";
	#mem
	print "<div style=\"position:absolute;left:50px;top:50px;\">\n";
	print "<input \n";
	print "class=\"knob\"\n";
	print "data-angleOffset=\"144\"\n";
	print "data-bgColor=\"#".$html_circle_bcolor2."\"\n";
	print "data-fgColor=\"#".$html_circle_color3_2."\"\n";
	print "data-width=\"150\"\n";
	print "data-readOnly=true\n";
	print "value=\"$para_mem3\"\n";
	print "data-min=\"0\"\n";
	print "data-max=\"100\"\n";
	print "data-displayInput=false\n";
	print "data-thickness=\".07\"\n";
	print ">\n";
	print "</div>\n";
	#la
	print "<div style=\"position:absolute;left:55px;top:55px;\">\n";
	print "<input \n";
	print "class=\"knob para_la\"\n";
	print "data-angleOffset=\"216\"\n";
	print "data-bgColor=\"#".$html_circle_bcolor2."\"\n";
	print "data-fgColor=\"#".$html_circle_color3_3."\"\n";
	print "data-width=\"140\"\n";
	print "data-readOnly=true\n";
	print "value=\"$para_la\"\n";
	print "data-min=\"0\"\n";
	print "data-max=\"1\"\n";
	print "data-displayInput=false\n";
	print "data-thickness=\".075\"\n";
	print ">\n";
	print "</div>\n";
	#volt
	print "<div style=\"position:absolute;left:60px;top:60px;\">\n";
	print "<input \n";
	print "class=\"knob\"\n";
	print "data-angleOffset=\"288\"\n";
	print "data-bgColor=\"#".$html_circle_bcolor2."\"\n";
	print "data-fgColor=\"#".$html_circle_color3_4."\"\n";
	print "data-width=\"130\"\n";
	print "data-readOnly=true\n";
	print "value=\"$para_volt\"\n";
	print "data-min=\"0\"\n";
	print "data-max=\"2\"\n";
	print "data-displayInput=false\n";
	print "data-thickness=\".08\"\n";
	print ">\n";
	print "</div>\n";
	#tmp
	print "<div style=\"position:absolute;left:65px;top:65px;\">\n";
	print "<input \n";
	print "class=\"knob\"\n";
	print "data-angleOffset=\"0\"\n";
	print "data-bgColor=\"#".$html_circle_bcolor2."\"\n";
	print "data-fgColor=\"#".$html_circle_color3_5."\"\n";
	print "data-width=\"120\"\n";
	print "data-readOnly=true\n";
	print "value=\"$para_tmp\"\n";
	print "data-min=\"0\"\n";
	print "data-max=\"100\"\n";
	print "data-displayInput=false\n";
	print "data-thickness=\".085\"\n";
	print ">\n";
	print "</div>\n";
	#status
	print "<div style=\"position:absolute;left:75px;top:75px;\">\n";
	print "<input \n";
	print "class=\"knob\"\n";
	print "data-angleOffset=\"0\"\n";
	print "data-bgColor=\"none\"\n";
	print "data-fgColor=\"#".$html_circle_color5."\"\n";
	print "data-width=\"100\"\n";
	print "data-readOnly=true\n";
	print "value=\"100\"\n";
	print "data-min=\"0\"\n";
	print "data-max=\"100\"\n";
	print "data-displayInput=false\n";
	print "data-thickness=\".03\"\n";
	print ">\n";
	print "</div>\n";
	#vol1
	print "<div style=\"position:absolute;left:100px;top:100px;\">\n";
	print "<input \n";
	print "class=\"knob\"\n";
	print "data-angleOffset=\"0\"\n";
	print "data-bgColor=\"#".$html_circle_bcolor2."\"\n";
	print "data-fgColor=\"#".$html_circle_color4."\"\n";
	print "data-width=\"50\"\n";
	print "data-readOnly=true\n";
	print "value=\"$para_vol1\"\n";
	print "data-min=\"0\"\n";
	print "data-max=\"100\"\n";
	print "data-displayInput=false\n";
	print "data-thickness=\".2\"\n";
	print ">\n";
	print "</div>\n";
	#vol2
	print "<div style=\"position:absolute;left:105px;top:105px;\">\n";
	print "<input \n";
	print "class=\"knob\"\n";
	print "data-angleOffset=\"180\"\n";
	print "data-bgColor=\"#".$html_circle_bcolor2."\"\n";
	print "data-fgColor=\"#".$html_circle_color4."\"\n";
	print "data-width=\"40\"\n";
	print "data-readOnly=true\n";
	print "value=\"$para_vol2\"\n";
	print "data-min=\"0\"\n";
	print "data-max=\"100\"\n";
	print "data-displayInput=false\n";
	print "data-thickness=\".24\"\n";
	print ">\n";
	print "</div>\n";
	print "</div>\n";
}
