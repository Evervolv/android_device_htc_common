# Copyright (C) 2009 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Emit commands needed for HTC devices during OTA installation
(installing the radio image)."""

import common
import re
import sha

def FullOTA_Assertions(info):
  AddBootloaderAssertion(info, info.input_zip)


def IncrementalOTA_Assertions(info):
  AddBootloaderAssertion(info, info.target_zip)


def AddBootloaderAssertion(info, input_zip):
  android_info = input_zip.read("OTA/android-info.txt")
  m = re.search(r"require\s+version-bootloader\s*=\s*(\S+)", android_info)
  if m:
    bootloaders = m.group(1).split("|")
    if "*" not in bootloaders:
      info.script.AssertSomeBootloader(*bootloaders)
    info.metadata["pre-bootloader"] = m.group(1)


def InstallRadio(radio_img, api_version, input_zip, info):
  common.ZipWriteStr(info.output_zip, "radio.img", radio_img)

  if api_version >= 3:
    bitmap_txt = input_zip.read("RADIO/bitmap_size.txt")
    install_img = input_zip.read("RADIO/firmware_install.565")
    error_img = input_zip.read("RADIO/firmware_error.565")
    width, height, bpp = bitmap_txt.split()

    radio_sha = sha.sha(radio_img).hexdigest()

    info.script.UnmountAll()
    info.script.AppendExtra(('''
assert(htc.install_radio(package_extract_file("radio.img"),
                         %(width)s, %(height)s, %(bpp)s,
                         package_extract_file("install.565"),
                         package_extract_file("error.565"),
                         %(radio_sha)s));
''' % locals()).lstrip())

    common.ZipWriteStr(info.output_zip, "install.565", install_img)
    common.ZipWriteStr(info.output_zip, "error.565", error_img)
  elif info.input_version >= 2:
    info.script.AppendExtra(
        'write_firmware_image("PACKAGE:radio.img", "radio");')
  else:
    info.script.AppendExtra(
        ('assert(package_extract_file("radio.img", "/tmp/radio.img"),\n'
         '       write_firmware_image("/tmp/radio.img", "radio"));\n'))


def FullOTA_InstallEnd(info):
  try:
    radio_img = info.input_zip.read("RADIO/radio.img")
  except KeyError:
    print "warning: no radio image in input target_files; not flashing radio"
    return

  info.script.Print("Writing radio image...")

  InstallRadio(radio_img, info.input_version, info.input_zip, info)


def IncrementalOTA_InstallEnd(info):
  try:
    target_radio = info.target_zip.read("RADIO/radio.img")
  except KeyError:
    print "warning: radio image missing from target; not flashing radio"
    return

  try:
    source_radio = info.source_zip.read("RADIO/radio.img")
  except KeyError:
    source_radio = None

  if source_radio == target_radio:
    print "Radio image unchanged; skipping"
    return

  InstallRadio(target_radio, info.target_version, info.target_zip, info)
