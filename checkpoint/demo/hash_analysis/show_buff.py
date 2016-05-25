#!/usr/bin/env python
import sys

def show_printable(ch_list):
	output=""
	for ch in ch_list:
		if ch:
			try:
				char = chr(int(ch,16))
				output=output+char
			except Exception as e:
				pass
	print output
				
	
for line in sys.stdin:
	if not line:
		break
	if line.startswith("[show_buff]"):
		parts = line.split("#")
		if len(parts) == 3:
			ch_list = parts[1].split(",")
			#print ch_list
			show_printable(ch_list)

