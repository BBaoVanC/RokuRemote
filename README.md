# rokuremote
Comfortably control your Roku using your keyboard using (mostly) one hand.

## Installation

* Install Python dependencies:

```
pip3 install readchar
```

* Download the source code:

```
git clone https://github.com/leon-anavi/RokuRemote.git
```

* Run `rokuremote`:

```
python3 rokuremote.py
```

## Usage

* Connect from your computer to a Roku in the same network using the IP:

```
$ python3 rokuremote.py 
Loading default layout: layouts.default
Loaded layout: default
Author: bbaovanc
Description: Vim-inspired layout that requires a single hand for most gestures.
Enter IP of the Roku you want to control: 192.168.5.168
-- NORMAL MODE (press q to quit) --
```

* Enter command mode and select a layout, for example `intuitive`:

```
-- NORMAL MODE (press q to quit) --
Read: :
-- COMMAND MODE --
:setlayout intuitive
Loaded layout: intuitive
Author: bbaovanc
Description: Layout built to be intuitive and simple to use
-- NORMAL MODE (press q to quit) --
```

* Use the keys defined in the selected layoyt to control Roku from the keyboard of your computer.
