#!/usr/bin/env python3
'''
Created at: 2023-06-15
Updated at: 2023-06-15
Created by: Mka0001 <mka00000001@gmail.com>
Version: v0.0.1

This script (wrapper) grabs the output of `rsync` command (what called with `--info=progress2` and `-v` arguments) and produces a well-looking progress bar from it.

Help:
`./rsync_wrapper.py --help`
'''
from datetime import datetime
import argparse
import os
import re
import subprocess

try:
  from tqdm import tqdm
except ImportError:
  raise ImportError('`tqdm` module is required, but not installed on your system. Install it with `pip install tqdm` command.')

try:
  import cursor
except ImportError:
  raise ImportError('`cursor` module is required, but not installed on your system. Install it with `pip install cursor` command.')


units = ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi']


def b_to_h(size: int|float, format: str='.2f') -> str:
  '''Converts bytes to human readeable format. E.g.: `51000` -> `49.80 KiB`.
  
  size: required, size in bytes.
  format: optional, format of number part of `return`, default is `.2f`.
  return: Human readeable `size`, e.g.: `49.80 KiB`.
  '''
  if not isinstance(size, (int, float)):
    raise ValueError(f'`Size` type is `{type(size)}`, but only `int` or `float` is allowed. `Size` value is: `{size}`.')

  for unit in units:
    if abs(size) < 973 or unit == units[-1]:  # 973 bytes ~= 0.95 KiB.
      return f'{size:{format}} {unit}B'
    
    size /= 1024


LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'

# Step: Get terminal dimensions.
terminal_width = os.get_terminal_size().columns
terminal_height = os.get_terminal_size().lines

# Step: Check if terminal is big enough for progress bar.
min_required_width, min_required_height = 75, 7

message = 'The terminal {dim} is too small to accommodate the progress bar. Minimum required {dim} is {size} unit.'

if terminal_width < min_required_width:
  raise SystemError(message.format(dim='width', size=min_required_width))

if terminal_height < min_required_height:
  raise SystemError(message.format(dim='height', size=min_required_height))

# Step: Handling arguments.
parser = argparse.ArgumentParser()

parser.add_argument(
  '--rsync-command', '-r',
  type=str,
  required=True,
  help='The `rsync` command what you want to run, e.g.: `rsync -r ~/Documents/file.txt ~/Documents/file_copy.txt `.'
)

parser.add_argument(
  '--disable-progressbar', '-p',
  action=argparse.BooleanOptionalAction,
  help="Would you like to view progress bar? If you omit this argument, progress bar  will be displayed; otherwise, it will be hidden."
)

parser.add_argument(
  '--disable-sizeinfo', '-s',
  action=argparse.BooleanOptionalAction,
  help="Would you like to view the size information? If you omit this argument, the size information will be displayed; otherwise, it will be hidden."
)

parser.add_argument(
  '--disable-fileinfo', '-f',
  action=argparse.BooleanOptionalAction,
  help="Would you like to view the file information? If you omit this argument, the file information will be displayed; otherwise, it will be hidden."
)

args = parser.parse_args()

# Step: Check if `-r` argument is presented correctly.
if not args.rsync_command.startswith('rsync ') and not args.rsync_command.startswith('sudo rsync '):
  raise SyntaxError("You've presented an INVALID `rsync` COMMAND. Fix, and run it again!")

# Step: Set patterns. Note: We need to use `exclude_lines` later, because we only want to print out lines via `pbar_info` that contains filepaths. For samples see `./samples.txt`. Note: The thousand separator can be either a period (.) or a comma (,) depending on the language and regional settings.
total_size_pattern = re.compile(r'Total transferred file size: (?P<size>.*?) bytes')
currently_processed_size_pattern = re.compile(r'^(?P<size>.*?[0-9].*?) .*?%')
exclude_lines = re.compile(r'^(sending|\[sender\]|delta|size|total)')

# Step: Settings for tqdm progress bars.
l_bar = '{percentage:6.2f}% |'
r_bar = '| [El: {elapsed}; Rem: {remaining}; ETA: {eta:%Y-%m-%d %H:%M:%S}]'
bar_format = f'{l_bar}{{bar}}{r_bar}'

# Pbar progress.
pbar_progress_details = {
  'bar_format': bar_format,
  'position': 0
}

# Pbar size.
pbar_size_desc_pattern = 'Processed: {processed}; Remaining: {remaining}; Total: {total}; Speed: {speed}/s.'

if terminal_width < 100:
  pbar_size_desc_pattern = 'El/Rem/Tot: {processed} / {remaining} / {total}; Speed: {speed}/s.'

pbar_size_details = {
  'bar_format': '{desc}',
  'leave': False,
  'position': 1
}

# Pbar file.
prefix = 'File: '
max_desc_len = terminal_width - len(prefix) - 2

pbar_info_details = {
  'bar_format': f'{prefix}{{desc:.{max_desc_len}s}}',
  'leave': False,
  'position': 2
}

# Step: Retrieve the total size of the files in bytes. To accomplish this, we need to run `rsync` with `--dry-run` and `--stats`. Set the `total` value of `pbar_progress_details`.
cursor.hide()
print('Calculating the total size of the files. This process may take some time, so please be patient...')
cursor.show()

rsync_command_dry_run = args.rsync_command
for argument in ['--dry-run', '--stats']:
  if argument in rsync_command_dry_run: continue
  rsync_command_dry_run = rsync_command_dry_run.replace('rsync', f'rsync {argument}', 1)

result = subprocess.run(
  rsync_command_dry_run,
  stdout=subprocess.PIPE,
  shell=True,
  encoding='utf-8'
)

try:
  total_size_in_bytes = total_size_pattern.search(result.stdout)['size']
  total_size_in_bytes = int(''.join(char for char in total_size_in_bytes if char.isdigit()))
except:
  raise ValueError('Total file size determination failed.')

pbar_progress_details['total'] = total_size_in_bytes

print(LINE_UP, end=LINE_CLEAR)

# Step: Run `rsync` command as a separate process with `--info=progress2` and `-v` arguments, so we will have progress info and verbose output which contains file paths (and additional information).
rsync_command_verbose = args.rsync_command
for argument in ['--info=progress2', '-v']:
  if argument in rsync_command_verbose: continue
  rsync_command_verbose = rsync_command_verbose.replace('rsync', f'rsync {argument}', 1)

process = subprocess.Popen(
  rsync_command_verbose,
  stdout=subprocess.PIPE,
  stderr=subprocess.PIPE,
  shell=True,
  encoding='utf-8'
)

# Step: Read the live output stream of the process and display a progress bar based on the output. Hide the cursor while the progress bar is being presented.
cursor.hide()

progress_snapshots = []

if args.disable_progressbar: pbar_progress_details['disable'] = True
if args.disable_sizeinfo: pbar_size_details['disable'] = True
if args.disable_fileinfo: pbar_info_details['disable'] = True

with (
  tqdm(**pbar_progress_details) as pbar_progress,
  tqdm(**pbar_size_details) as pbar_size,
  tqdm(**pbar_info_details) as pbar_info
):
  for line in process.stdout:
    if not line: continue

    try:
      # Extract the processed size in bytes from `rsync` output.
      processed_size_in_bytes = currently_processed_size_pattern.search(line)['size']
      processed_size_in_bytes = int(''.join(char for char in processed_size_in_bytes if char.isdigit()))

      # Calculate progress speed.
      progress_snapshots.append({
        'at': datetime.now(),
        'processed_size_bytes': processed_size_in_bytes
      })
      progress_snapshots = progress_snapshots[-50:]

      progress_speed_bps = 0
      if len(progress_snapshots) > 1:
        sec_diff = (progress_snapshots[-1]['at'] - progress_snapshots[0]['at']).total_seconds()
        byte_diff = progress_snapshots[-1]['processed_size_bytes'] - progress_snapshots[0]['processed_size_bytes']

        progress_speed_bps = byte_diff / sec_diff

      # Refresh main progress bar.
      pbar_progress.n = processed_size_in_bytes
      pbar_progress.refresh()

      # Refresh size info of the progress bar.
      pbar_size.set_description_str(
        pbar_size_desc_pattern.format(
          processed = b_to_h(processed_size_in_bytes),
          remaining = b_to_h(total_size_in_bytes - processed_size_in_bytes),
          total = b_to_h(total_size_in_bytes),
          speed = b_to_h(progress_speed_bps)
        )
      )
    except TypeError:
      # This exception occurs when the current line doesn't contain size information. Other words: `search` result is `None`.
      # We set `-v` argument above for `rsync`, what means, `verbose`. Thanks to this, the command prints out the path of the currently processed file. Therefore, we can display the file path accordingly. Note: The verbose output includes additional information besides just file paths. That's why we are using the `exclude_lines` pattern to filter out those lines and focus only on the file paths.
      line_normalized = line.strip('\n')
      
      if not line_normalized: continue
      if exclude_lines.search(line_normalized): continue
  
      # Refresh file info of progress bar.
      pbar_info.set_description_str(line_normalized)
    except:
      raise ValueError(f'There was an error during processing `rsync` output. Affected line: `{line}`.')

cursor.show()

# Step: Why need this `print`? If you run `this wrapper` with `-p` argument, after `wrapper` is finished, next command line would start at the middle of the line. By implementing this approach, we can prevent the occurrence of this unwanted behavior.
if args.disable_progressbar: print(end='\r')

# Step: Print any errors, if present.
_, err = process.communicate()
if err:
  print('Error(s) occured while running `rsync` process:')
  print(err)
