# import socket

# addr_range = "192.168.1.%d"

# ip_address_up = []

# # Use UDP. 
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# s.settimeout(.5)

# for i in range(1, 254):
# 	print('here')
# 	try:
# 		ip = addr_range % i
# 		socket.gethostbyaddr(ip)
# 		ip_address_up.append(ip)
# 	except socket.herror as ex:
# 		pass

# print ip_address_up


import socket

print [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1]