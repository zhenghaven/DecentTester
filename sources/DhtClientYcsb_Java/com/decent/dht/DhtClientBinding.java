package com.decent.dht;

public class DhtClientBinding
{
	static
	{
		System.loadLibrary("DhtClientYcsb_App"); // Load native library.
	}

	public DhtClientBinding()
	{
		this.cPtr = 0;
	}

	public native void init(long maxOpPerTicket) throws DhtClientBindingException;

	public native void cleanup() throws DhtClientBindingException;

	public native String read(String key) throws DhtClientBindingException;

	public native void insert(String key, String value) throws DhtClientBindingException;

	public native void update(String key, String value) throws DhtClientBindingException;

	public native void delete(String key) throws DhtClientBindingException;

	private long cPtr;

}