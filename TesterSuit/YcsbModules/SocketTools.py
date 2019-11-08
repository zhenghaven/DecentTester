import struct

def SocketRecvall(conn, length):

	bytes = b''

	while len(bytes) != length:
		tmpBytes = conn.recv(length - len(bytes))
		if len(tmpBytes) == 0:
			raise RuntimeError('Connection is closed by peer.')
		bytes = bytes + tmpBytes

	return bytes

def SocketSend_uint64(conn, num):

	bytes = struct.pack('<Q', num)
	conn.sendall(bytes)

def SocketRecv_uint64(conn):

	bytes = SocketRecvall(conn, 8)

	return struct.unpack('<Q', bytes)[0]

def SocketSendPack(conn, str):

	bstr = str.encode()

	SocketSend_uint64(conn, len(bstr))
	conn.sendall(bstr)

def SocketRecvPack(conn):

	bstrLen = SocketRecv_uint64(conn)

	return SocketRecvall(conn, bstrLen).decode()
