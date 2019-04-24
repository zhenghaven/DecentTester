package com.Decent;

public class DhtClientBinding
{
	static
	{
		System.loadLibrary("DhtClientYcsb_App"); // Load native library.
	}

	public static native void init() throws DhtClientBindingException;

	public static native void cleanup() throws DhtClientBindingException;

	public static native String read(String key) throws DhtClientBindingException;

	public static native void insert(String key, String value) throws DhtClientBindingException;

	public static native void delete(String key) throws DhtClientBindingException;

}