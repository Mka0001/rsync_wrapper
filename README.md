# A simple wrapper for [rsync](https://rsync.samba.org/) that shows an improved progress bar

`Rsync` is a fast, versatile, remote (and local) file-copying tool. There are two types of progress bars available for `rsync`. You can view these bars by using either the `--progress` or `--info=progress2` arguments. None of them looks too good (subjective view). This script helps to display an improved progress bar. For this, you need to wrap `rsync` command like this:

```sh
./rsync_wrapper -r "rsync ~/Documents/file.txt ~/Documents/file_copy.txt"
```

## Output will look like this:
```sh
40.00% |█████████           | [El: 00:02; Rem: 00:03; ETA: 2023-06-16 10:01:02]
Processed: 0.10 GiB; Remaining: 0.14 GiB; Total: 0.24 GiB; Speed: 25.50 MiB/s.
File: Test.txt
```

## As you can see, the output contains three rows:
- 1st: The progress bar with elapsed, remaining, and ETA times.
- 2nd: Size info, what shows transferred, remaining and total size of files. This row also shows the transfer speed.
- 3rd: Currently transferring file.

## To display help, type:
```sh
./rsync_wrapper.py --help
```

## Arguments:
- -r (required): The `rsync` command between double quotes. This is the only required command.
- -p (optional): If presented, progress bar will be hidden.
- -s (optional): If presented, size info will be hidden.
- -f (optional): If presented, file info will be hidden.

## Usage examples:
### Example 1:
Run `wrapper` and `rsync` as normal user (You can copy only your own files):
```sh
./rsync_wrapper.py -r "rsync ~/Documents/file.txt ~/Documents/file_copy.txt"
```

### Example 2:
Run `wrapper` as normal user, but run `rsync` as superuser (You can copy any files):
```sh
./rsync_wrapper.py -r "sudo rsync ~/Documents/file.txt ~/Documents/file_copy.txt"
```

### Example 3:
Run `wrapper` and `rsync` as superuser (You can copy any files):
```sh
sudo ./rsync_wrapper.py -r "sudo rsync ~/Documents/file.txt ~/Documents/file_copy.txt"
```

### Example 4:
Hide size info (`-s`) and file info (`-f`) lines:
```sh
./rsync_wrapper.py -fsr "rsync ~/Documents/file.txt ~/Documents/file_copy.txt"
```

## Test information:
Has been tested on `Ubuntu v22.04` with `Python v3.11` interpreter.
