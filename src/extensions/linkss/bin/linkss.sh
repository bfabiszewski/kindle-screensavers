#!/bin/sh
#
# KUAL ScreenSavers actions helper script
#
# $Id: linkss.sh 16254 2019-07-23 21:58:00Z NiLuJe $
#
##

# Get hackname from the script's path (NOTE: Will only work for scripts called from /mnt/us/extensions/${KH_HACKNAME})
KH_HACKNAME="${PWD##/mnt/us/extensions/}"

# Try to pull our custom helper lib
libkh_fail="false"
# Handle both the K5 & legacy helper, so I don't have to maintain the exact same thing in two different places :P
for my_libkh in libkh5 libkh ; do
	_KH_FUNCS="/mnt/us/${KH_HACKNAME}/bin/${my_libkh}"
	if [ -f ${_KH_FUNCS} ] ; then
		. ${_KH_FUNCS}
		# Got it, go away!
		libkh_fail="false"
		break
	else
		libkh_fail="true"
	fi
done

if [ "${libkh_fail}" == "true" ] ; then
	# Pull default helper functions for logging
	_FUNCTIONS=/etc/rc.d/functions
	[ -f ${_FUNCTIONS} ] && . ${_FUNCTIONS}
	# We couldn't get our custom lib, abort
	msg "couldn't source libkh5 nor libkh from '${KH_HACKNAME}'" W
	exit 0
fi

# We need the proper privileges...
if [ "$(id -u)" -ne 0 ] ; then
	kh_msg "unprivileged user, aborting" E v
	exit 1
fi

## Enable a specific trigger file in the hack's basedir
# Arg 1 is exact config trigger file name
##
enable_hack_trigger_file()
{
	if [ $# -lt 1 ] ; then
		kh_msg "not enough arguments passed to enable_hack_trigger_file ($# while we need at least 1)" W v "missing trigger file name"
	fi

	kh_trigger_file="${KH_HACK_BASEDIR}/${1}"

	touch "${kh_trigger_file}"
}

## Remove a specific trigger file in the hack's basedir
# Arg 1 is exact config trigger file name
##
disable_hack_trigger_file()
{
	if [ $# -lt 1 ] ; then
		kh_msg "not enough arguments passed to disable_hack_trigger_file ($# while we need at least 1)" W v "missing trigger file name"
		return 1
	fi

	kh_trigger_file="${KH_HACK_BASEDIR}/${1}"

	rm -f "${kh_trigger_file}"
}

## Check if we're a Touch device (>= K5)
check_is_touch_device()
{
	[ "${IS_K5}" == "true" ] && return 0
	[ "${IS_TOUCH}" == "true" ] && return 0
	[ "${IS_PW}" == "true" ] && return 0
	[ "${IS_PW2}" == "true" ] && return 0
	[ "${IS_KV}" == "true" ] && return 0
	[ "${IS_KT2}" == "true" ] && return 0
	[ "${IS_PW3}" == "true" ] && return 0
	[ "${IS_KOA}" == "true" ] && return 0
	[ "${IS_KT3}" == "true" ] && return 0
	[ "${IS_KOA2}" == "true" ] && return 0
	[ "${IS_PW4}" == "true" ] && return 0
	[ "${IS_KT4}" == "true" ] && return 0
	[ "${IS_KOA3}" == "true" ] && return 0

	# We're not!
	return 1
}

## Check if we're a PW
check_is_pw_device()
{
	[ "${IS_PW}" == "true" ] && return 0

	# We're not!
	return 1
}

## Check if we're a KV
check_is_kv_device()
{
	[ "${IS_KV}" == "true" ] && return 0

	# We're not!
	return 1
}

## Check if we're running FW >= 5.5
check_is_fw55_device()
{
	[ "${K5_ATLEAST_55}" == "true" ] && return 0

	# We're not!
	return 1
}

## Check if we're a Waterstones PW
check_is_waterstones_device()
{
	# NOTE: The KT2 & KV both did away with the size hint... So did FW 5.6 on the PW2, so ties this to the FW version first...
	if check_is_fw55_device ; then
		# FIXME?
		if [ -f "/var/local/custom_screensavers/bg_ss00.png" ] ; then
			return 0
		fi
	elif check_is_pw_device ; then
		# FIXME?
		if [ -f "/var/local/custom_screensavers/bg_medium_ss00.png" ] ; then
			return 0
		fi
	elif check_is_kv_device ; then
		# FIXME?
		if [ -f "/var/local/custom_screensavers/bg_ss00.png" ] ; then
			return 0
		fi
	else
		# FIXME?
		if [ -f "/var/local/custom_screensavers/bg_xsmall_ss00.png" ] ; then
			return 0
		fi
	fi

	# We're not!
	return 1
}

## Enable at boot
enable_auto()
{
	enable_hack_trigger_file "auto"
	# FIXME: Workaround broken? custom status message by using eips ourselves. Kill this once it works properly.
	kh_msg "Enable the ScreenSavers Hack" I a
}

## Disable at boot
disable_auto()
{
	disable_hack_trigger_file "auto"
	kh_msg "Disable the ScreenSavers Hack" I a
}

## Enable verbose mode
enable_verbose()
{
	enable_hack_trigger_file "verbose"
	kh_msg "Make the ScreenSavers Hack verbose" I a
}

## Disable verbose mode
disable_verbose()
{
	disable_hack_trigger_file "verbose"
	kh_msg "Make the ScreenSavers Hack quiet" I a
}

## Enable complete uninstall flag
enable_uninstall()
{
	enable_hack_trigger_file "uninstall"
	kh_msg "Flag ScreenSavers for complete uninstall" I a
}

## Disable complete uninstall flag
disable_uninstall()
{
	disable_hack_trigger_file "uninstall"
	kh_msg "Restore default ScreenSavers uninstall behavior" I a
}

## Enable Waterstones workaround
enable_beta()
{
	# Only applicable to Waterstones devices!
	if ! check_is_waterstones_device ; then
		kh_msg "This is not applicable to your device" W v
		return 1
	fi

	enable_hack_trigger_file "beta"
	kh_msg "Try to workaround the Waterstones screensaver" I a
}

## Disable Waterstones workaround
disable_beta()
{
	# Be more lenient on the disable side, only check for FW >= 5.5 or a PW/KV
	if ! check_is_fw55_device && ! check_is_pw_device && ! check_is_kv_device ; then
		kh_msg "This is not applicable to your device" W v
		return 1
	fi

	disable_hack_trigger_file "beta"
	kh_msg "Disable Waterstones support" I a
}

## Enable autoreboot feature
enable_autoreboot()
{
	# The menu checks both SS & Linkfonts, so, create both if the Fonts hack is installed, it will take precedence anyway
	if [ -d "/mnt/us/linkfonts" ] ; then
		touch "/mnt/us/linkfonts/autoreboot"
	fi
	enable_hack_trigger_file "autoreboot"
	kh_msg "Enable the autoreboot feature" I a
}

## Disable verbose mode
disable_autoreboot()
{
	# And for the same reason, handle the Fonts trigger file, too
	if [ -f "/mnt/us/linkfonts/autoreboot" ] ; then
		rm -f "/mnt/us/linkfonts/autoreboot"
	fi
	disable_hack_trigger_file "autoreboot"
	kh_msg "Disable the autoreboot feature" I a
}

## Trigger autoreboot feature
trigger_autoreboot()
{
	# We have to be a bit smarter here, because if the Fonts hack is installed, its watchdog takes precedence over ours
	if [ -f "/mnt/us/linkfonts/run/usb-watchdog.pid" ] ; then
		touch "/mnt/us/linkfonts/reboot"
		kh_msg "Trigger a framework restart the next time device is unplugged (linkfonts)" I a "trigger a framework restart at unplug (via F)"
		return 0
	fi
	# Sanity check, check that there is at least one watchdog running (here, ours)
	if [ -f "${WATCHDOG_PID}" ] ; then
		enable_hack_trigger_file "reboot"
		kh_msg "Trigger a framework restart the next time device is unplugged (${KH_HACKNAME})" I a "trigger a framework restart at unplug (via S)"
		return 0
	fi

	# If we're here, then there's no watchdog running, do nothing, and print a warning
	kh_msg "Cannot do that without a watchdog running! Enable the autoreboot feature first?" W v "autoreboot feature not enabled"
	return 1
}

## Abort scheduled autoreboot
abort_autoreboot()
{
	# Handle both hacks, again
	if [ -f "/mnt/us/linkfonts/reboot" ] ; then
		rm -f "/mnt/us/linkfonts/reboot"
	fi
	if [ -f "${KH_HACK_BASEDIR}/reboot" ] ; then
		disable_hack_trigger_file "reboot"
	fi
	kh_msg "Abort the framework restart scheduled the next time the device is unplugged" I a "framework restart unscheduled"
}

## Restart framework...
framework_restart()
{
	# Sleep a while to let KUAL die
	kh_msg "Hush, little baby . . ." I a
	sleep 5

	# Restart!
	kh_msg "Framework restart . . ." I v

	# FW >= 5.x
	if check_is_touch_device ; then
		# Show the splash screen...
		. /etc/upstart/splash
		splash_cleanup
		splash_init || kh_msg "cannot init splash module" E a
		splash_progress 0

		# Survive the mass killing so we can properly update the progress bar...
		trap "" SIGTERM

		# Do a stop & start instead of a restart because restart doesn't go through the 'stopped' phase, and we rely on it for our stop on stanza...
		# Cf. http://upstart.ubuntu.com/cookbook/#restart restart != stop && start.
		stop framework
		sync
		start framework

		# And, apparently, we have to do everything ourselves...
		for splash_bar in $(seq 1 25) ; do
			splash_progress $((splash_bar * 4))
			sleep 1
		done
	else
		# If the ScreenSavers hack is enabled, do the same tasks an autoreboot would...
		if [ -f "${LINKSS_BASEDIR}/auto" ] ; then
			kh_msg "Custom ScreenSavers check . . ." I a
			${LINKSS_SHUFFLE} watchdog
		fi
		# Sync, just to be safe
		sync

		/etc/init.d/framework restart
	fi
}

## Switch to Image Cycle mode
mode_cycle()
{
	# It's the default, so just clear every other mode ;)
	for ss_mode in cover last random shuffle ; do
		[ -f "${KH_HACK_BASEDIR}/${ss_mode}" ] && disable_hack_trigger_file "${ss_mode}"
	done
	kh_msg "Use custom images as ScreenSavers" I a
}

## Switch to Random Image Cycle mode
mode_cycle_random()
{
	# To keep things tidy, make sure we're in cycle mode first
	for ss_mode in cover last ; do
		[ -f "${KH_HACK_BASEDIR}/${ss_mode}" ] && disable_hack_trigger_file "${ss_mode}"
	done
	# Then enable the random variant
	enable_hack_trigger_file "random"
	kh_msg "Use custom images in a random order as ScreenSavers" I a "Use random custom images as ScreenSavers"
}

## Switch to Shuffled Image Cycle mode
mode_cycle_shuffle()
{
	# To keep things tidy, make sure we're in cycle mode first
	for ss_mode in cover last ; do
		[ -f "${KH_HACK_BASEDIR}/${ss_mode}" ] && disable_hack_trigger_file "${ss_mode}"
	done
	# Then enable the shuffle variant
	enable_hack_trigger_file "shuffle"
	kh_msg "Shuffle custom ScreenSavers images on autoreboots" I a "Shuffle ScreenSavers on autoreboots"
}

## Switch to Last Screen mode
mode_last()
{
	# Only available on FW >= 5!
	if ! check_is_touch_device ; then
		kh_msg "This is not supported on your device" W v
		return 1
	fi

	# Keep things tidy
	for ss_mode in cover random shuffle ; do
		[ -f "${KH_HACK_BASEDIR}/${ss_mode}" ] && disable_hack_trigger_file "${ss_mode}"
	done

	# Then enable it
	enable_hack_trigger_file "last"
	kh_msg "Use the last screen shown as ScreenSaver" I a
}

## Switch to Cover mode
mode_cover()
{
	# Keep things tidy
	for ss_mode in last random shuffle ; do
		[ -f "${KH_HACK_BASEDIR}/${ss_mode}" ] && disable_hack_trigger_file "${ss_mode}"
	done

	# Then enable it
	enable_hack_trigger_file "cover"
	kh_msg "Cover mode requires a framework restart" I v
}

## Use white letterboxing borders
white_borders()
{
	# It's the default, so just clear every other settings ;)
	for cover_mode in stretch autocrop black ; do
		[ -f "${KH_HACK_BASEDIR}/${cover_mode}" ] && disable_hack_trigger_file "${cover_mode}"
	done
	kh_msg "Use white borders around the cover" I a
}

## Use black letterboxing borders
black_borders()
{
	# Keep it tidy, make sure we're in letterbox mode ;)
	for cover_mode in stretch autocrop ; do
		[ -f "${KH_HACK_BASEDIR}/${cover_mode}" ] && disable_hack_trigger_file "${cover_mode}"
	done

	# Then enable black borders
	enable_hack_trigger_file "black"
	kh_msg "Use black borders around the cover" I a
}

## Switch to letterbox mode
letterbox_cover()
{
	# Keep it tidy, make sure we're in letterbox mode, but keep current border color setting ;)
	for cover_mode in stretch autocrop ; do
		[ -f "${KH_HACK_BASEDIR}/${cover_mode}" ] && disable_hack_trigger_file "${cover_mode}"
	done
	kh_msg "Keep cover aspect ratio" I a
}

## Switch to stretch mode
stretch_cover()
{
	# Keep it tidy, make sure we're not in another mode
	for cover_mode in autocrop ; do
		[ -f "${KH_HACK_BASEDIR}/${cover_mode}" ] && disable_hack_trigger_file "${cover_mode}"
	done

	# Then enable it
	enable_hack_trigger_file "stretch"
	kh_msg "Stretch cover to fill the screen, disregarding aspect ratio" I a "Stretch cover to screen aspect"
}

## Switch to autocrop mode
autocrop_cover()
{
	# Keep it tidy, make sure we're not in another mode
	for cover_mode in stretch ; do
		[ -f "${KH_HACK_BASEDIR}/${cover_mode}" ] && disable_hack_trigger_file "${cover_mode}"
	done

	# Then enable it
	enable_hack_trigger_file "autocrop"
	kh_msg "Zoom cover to fill the screen, keep aspect ratio by autocropping borders" I a "Zoom and autocrop cover"
}

## Enable first sleep cycle after a book switch workaround
enable_sleep()
{
	# Only applicable to legacy devices!
	if check_is_touch_device ; then
		kh_msg "This is not applicable to your device" W v
		return 1
	fi

	enable_hack_trigger_file "sleep"
	kh_msg "Enable a workaround for better accuracy of the first sleep cycle image after a book switch" I a "Enable sleep workaround"
}

## Disable first sleep cycle after a book switch workaround
disable_sleep()
{
	# Only applicable to legacy devices!
	if check_is_touch_device ; then
		kh_msg "This is not applicable to your device" W v
		return 1
	fi

	disable_hack_trigger_file "sleep"
	kh_msg "No specific workaround for first sleep cycle image" I a "Disable sleep workaround"
}

## Enable Personal Info watermark
enable_pinfo()
{
	# Only available on FW >= 5!
	if ! check_is_touch_device ; then
		kh_msg "This is not supported on your device" W v
		return 1
	fi

	enable_hack_trigger_file "pinfo"
	kh_msg "Add a watermark with your personal info at the bottom of the screen" I a "Enable personal info watermark"
}

## Disable Personal Info watermark
disable_pinfo()
{
	# Only available on FW >= 5!
	if ! check_is_touch_device ; then
		kh_msg "This is not supported on your device" W v
		return 1
	fi

	disable_hack_trigger_file "pinfo"
	kh_msg "Remove the watermark with your personal info at the bottom of the screen" I a "Disable personal info watermark"
}

## Enable Low Memory Mode (skip software dithering)
enable_lowmem()
{
	# Keep it tidy, make sure we're not in another mode
	for dither_mode in riemersma ; do
		[ -f "${KH_HACK_BASEDIR}/${dither_mode}" ] && disable_hack_trigger_file "${dither_mode}"
	done

	enable_hack_trigger_file "lowmem"
	kh_msg "Skip the software dithering to keep memory consumption sane" I a "Skip software dithering"
}

## Disable Low memory Mode (enable FloydSteinberg software dithering)
disable_lowmem()
{
	# It's the default, so just clear every other setting ;)
	for dither_mode in lowmem riemersma ; do
		[ -f "${KH_HACK_BASEDIR}/${dither_mode}" ] && disable_hack_trigger_file "${dither_mode}"
	done

	kh_msg "Enable FloydSteinberg software dithering" I a
}

## Disable Low memory Mode (enable Riemersma software dithering)
disable_lowmem_riemersma()
{
	# Keep it tidy, make sure we're not in another mode
	for dither_mode in lowmem ; do
		[ -f "${KH_HACK_BASEDIR}/${dither_mode}" ] && disable_hack_trigger_file "${dither_mode}"
	done

	enable_hack_trigger_file "riemersma"
	kh_msg "Enable Riemersma software dithering" I a
}

## Enable periodicals handling
enable_periodicals()
{
	enable_hack_trigger_file "periodicals"
	kh_msg "Handle periodicals" I a
}

## Disable periodicals handling
disable_periodicals()
{
	disable_hack_trigger_file "periodicals"
	kh_msg "Do not handle periodicals" I a
}

## Preview the current cover
current_ss_preview()
{
	if [ ! -f "${KH_HACK_BASEDIR}/cover" ] ; then
		kh_msg "Must be in cover mode" W v
		return 1
	fi

	# Check that we have at least 8M free in /var (a PW fb dump is ~4.5MB)
	if [ "$(df -k /var | awk '$3 ~ /[0-9]+/ { print $4 }')" -lt "8192" ] ; then
		kh_msg "Not enough free space in /var" W v
		return 1
	fi

	# Here be dragons... Save a copy of the current fb, to restore it later...
	cat /dev/fb0 > /var/tmp/linkss-fb.dump

	kh_msg "Previewing current active cover for 10s..." I a
	# Wait a bit for everything to settle..
	sleep 1

	# Clear the screen, optionally without a full flash to make legacy eInk controllers happy...
	if check_is_touch_device ; then
		eips -f -c
	else
		eips -c
	fi
	usleep 750000
	# One more time, to kill the ghosting...
	if check_is_touch_device ; then
		eips -f -c
	else
		eips -c
	fi
	usleep 750000

	# Now, print the current active cover...
	for active_cover in /var/linkss/cover/* ; do
		[ -f "${active_cover}" ] && eips -f -g "${active_cover}"
	done

	# Sleep for 10s
	sleep 10

	# Restore fb
	cat /var/tmp/linkss-fb.dump > /dev/fb0
	rm -f /var/tmp/linkss-fb.dump

	# Refresh screen...
	eips ''
}

## Clear the cover cache
tools_clear_cover_cache()
{
	for cached_cover in ${KH_HACK_BASEDIR}/cover_cache/cover_*.png ; do
		# Do a test again, because ash will return our glob as-is if it doesn't match anything...
		[ -f "${cached_cover}" ] && rm -f "${cached_cover}"
	done

	kh_msg "All processed covers have been deleted" I a
}

## Clear the cached personal info overlay
tools_clear_pinfo_cache()
{
	# Only available on FW >= 5!
	if ! check_is_touch_device ; then
		kh_msg "This is not supported on your device" W v
		return 1
	fi

	[ -f "${KH_HACK_BASEDIR}/cover_cache/pinfo.png" ] && rm -f "${KH_HACK_BASEDIR}/cover_cache/pinfo.png"
	kh_msg "Cached personal info watermark deleted" I a
}

## Process images in the staging directory
tools_staging_process()
{
	# Only available on FW >= 5!
	if ! check_is_touch_device ; then
		kh_msg "This is not supported on your device" W v
		return 1
	fi

	kh_msg "Process staging images . . ." I a

	# Use the same settings as cover mode... Fugly code duplication ahead!
	# Letterbox color
	if [ -f "${LINKSS_BASEDIR}/black" ] ; then
		# We want black borders!
		lb_bg_color="black"
	else
		lb_bg_color="white"
	fi
	# Default to letterboxing, with correct AR
	resize_mode="letterbox"
	# Autocrop (centered)
	if [ -f "${LINKSS_BASEDIR}/autocrop" ] ; then
		resize_mode="autocrop"
	fi
	# Stretch
	if [ -f "${LINKSS_BASEDIR}/stretch" ] ; then
		resize_mode="stretch"
	fi
	# Dithering
	if [ -f "${LINKSS_BASEDIR}/riemersma" ] ; then
		dither_algo="Riemersma"
	else
		dither_algo="FloydSteinberg"
	fi
	# Die in a fire after 60s, to avoid looping like crazy if we're OOM.
	dither_args="-limit time 60 -dither ${dither_algo} -remap ${LINKSS_BASEDIR}/etc/kindle_colors.gif"
	# Make eips happy (it chokes on plain 16c images, it expects a true PNG8 [256c], *with* a 256c colormap)
	png8_args="-define png:color-type=0 -define png:bit-depth=8"

	# Setup our spinner for visual feedback...
	# eips can't print a backslash... -_-" Use an X in place of \
	SPINNER='|/-X'
	i=0
	# Ensure we have a blank line for our centered spinner
	kh_msg "" I v

	# And now loop over the staging directory...
	for cur_img in ${LINKSS_BASEDIR}/staging/* ; do
		if [ -f "${cur_img}" ] ; then
			# We're going to need the (base) filename of the image . . .
			cur_filename="${cur_img##*/}"

			# Don't process stuff twice...
			case "${cur_filename}" in
				# NOTE: Crappy busybox ash won't let me do wildcard matches in a bracket test...
				processed_*.png )
					kh_msg "'${cur_filename}' has already been processed, skipping." W q
					continue
				;;
			esac

			i=$((i+1))
			# Spin the spinner with magic ;)
			SPINNER="${SPINNER#?}${SPINNER%???}"
			CUR_SPIN="** $(printf '%.1s' "${SPINNER}") **"
			# Center it...
			eips $(((${EIPS_MAXCHARS} - ${#CUR_SPIN}) / 2)) $((${EIPS_MAXLINES} - 2)) "${CUR_SPIN}"

			kh_msg "Processing '${cur_filename}' . . ." I q
			# . . . and now without the file extension
			cur_filename="${cur_filename%.*}"

			# Follow the resize mode the user prefers (stretch, autocrop, or letterbox)
			case "${resize_mode}" in
				"stretch" )
					${LINKSS_BINDIR}/convert "${cur_img}" -filter LanczosSharp -resize "${MY_SCREEN_SIZE}!" -colorspace Gray ${dither_args} -quality 75 ${png8_args} "${LINKSS_BASEDIR}/staging/processed_${cur_filename}.png"
				;;
				"autocrop" )
					${LINKSS_BINDIR}/convert "${cur_img}" -filter LanczosSharp -resize "${MY_SCREEN_SIZE}^" -gravity center -extent "${MY_SCREEN_SIZE}" -colorspace Gray ${dither_args} -quality 75 ${png8_args} "${LINKSS_BASEDIR}/staging/processed_${cur_filename}.png"
				;;
				* )
					${LINKSS_BINDIR}/convert "${cur_img}" -filter LanczosSharp -resize "${MY_SCREEN_SIZE}" -background ${lb_bg_color} -gravity center -extent "${MY_SCREEN_SIZE}" -colorspace Gray ${dither_args} -quality 75 ${png8_args} "${LINKSS_BASEDIR}/staging/processed_${cur_filename}.png"
				;;
			esac

			# Delete original on success
			if [ $? -eq 0 ] ; then
				rm -f "${cur_img}"
				kh_msg ". . . Success!" I q
			else
				kh_msg ". . . Failed!" W q
			fi
		fi
	done

	# Warn on an empty directory (or one full of already processed images)
	if [ "${i}" -eq 0 ] ; then
		kh_msg "Nothing new to process" W v
	else
		kh_msg "Done" I v
	fi
}

## Reset to default settings
reset_trigger_files()
{
	# General mode
	for ss_mode in cover last random shuffle ; do
		[ -f "${KH_HACK_BASEDIR}/${ss_mode}" ] && disable_hack_trigger_file "${ss_mode}"
	done
	# Cover mode settings
	for cover_mode in stretch autocrop black ; do
		[ -f "${KH_HACK_BASEDIR}/${cover_mode}" ] && disable_hack_trigger_file "${cover_mode}"
	done
	# Dithering settings
	for dither_mode in lowmem riemersma ; do
		[ -f "${KH_HACK_BASEDIR}/${dither_mode}" ] && disable_hack_trigger_file "${dither_mode}"
	done

	kh_msg "Reset to default behavior" I a
}

## Print the version of the hack currently installed
show_version()
{
	if [ -f "${KH_HACK_BASEDIR}/etc/VERSION" ] ; then
		kh_msg "$(cat ${KH_HACK_BASEDIR}/etc/VERSION)" I v
	else
		kh_msg "No version info file" W v
	fi
}

## Main
case "${1}" in
	"enable_auto" )
		${1}
	;;
	"disable_auto" )
		${1}
	;;
	"enable_verbose" )
		${1}
	;;
	"disable_verbose" )
		${1}
	;;
	"enable_uninstall" )
		${1}
	;;
	"disable_uninstall" )
		${1}
	;;
        "enable_beta" )
		${1}
	;;
	"disable_beta" )
		${1}
	;;
	"enable_autoreboot" )
		${1}
	;;
	"disable_autoreboot" )
		${1}
	;;
	"trigger_autoreboot" )
		${1}
	;;
	"abort_autoreboot" )
		${1}
	;;
	"framework_restart" )
		${1}
	;;
	"mode_cycle" )
		${1}
	;;
	"mode_cycle_random" )
		${1}
	;;
	"mode_cycle_shuffle" )
		${1}
	;;
	"mode_last" )
		${1}
	;;
	"mode_cover" )
		${1}
	;;
	"white_borders" )
		${1}
	;;
	"black_borders" )
		${1}
	;;
	"letterbox_cover" )
		${1}
	;;
	"stretch_cover" )
		${1}
	;;
	"autocrop_cover" )
		${1}
	;;
	"enable_sleep" )
		${1}
	;;
	"disable_sleep" )
		${1}
	;;
	"enable_pinfo" )
		${1}
	;;
	"disable_pinfo" )
		${1}
	;;
	"enable_lowmem" )
		${1}
	;;
	"disable_lowmem" )
		${1}
	;;
        "disable_lowmem_riemersma" )
		${1}
	;;
	"enable_periodicals" )
		${1}
	;;
	"disable_periodicals" )
		${1}
	;;
	"current_ss_preview" )
		${1}
	;;
	"tools_clear_cover_cache" )
		${1}
	;;
	"tools_clear_pinfo_cache" )
		${1}
	;;
	"tools_staging_process" )
		${1}
	;;
	"reset_trigger_files" )
		${1}
	;;
	"show_version" )
		${1}
	;;
	* )
		kh_msg "invalid action (${1})" W v "invalid action"
	;;
esac
