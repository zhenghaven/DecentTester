package com.Decent;

public class DhtClientBinding
{
	static
	{
		System.loadLibrary("DhtClientYcsb_App"); // Load native library.
	}

	public static native boolean init();

	public static native boolean cleanup();

	public static native boolean read(String key, String value);

	public static native boolean insert(String key, String value);

	//public static boolean delete(String key);

}