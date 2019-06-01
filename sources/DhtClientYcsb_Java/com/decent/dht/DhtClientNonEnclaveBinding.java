package com.decent.dht;

public class DhtClientNonEnclaveBinding
{
	static
	{
		System.loadLibrary("DhtClientNonEnclaveYcsb_App"); // Load native library.
	}

	public DhtClientNonEnclaveBinding()
	{
		this.cPtr = 0;
	}

	public native void init() throws DhtClientBindingException;

	public native void cleanup() throws DhtClientBindingException;

	public native String read(String key) throws DhtClientBindingException;

	public native void insert(String key, String value) throws DhtClientBindingException;

	public native void update(String key, String value) throws DhtClientBindingException;

	public native void delete(String key) throws DhtClientBindingException;

	private long cPtr;

}