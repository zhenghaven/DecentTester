#include "../DhtClientYcsb_Java/com_decent_dht_DhtClientBinding.h"

#include <string>

#include "DhtClientApp.h"
#include "EnclaveInitializer.h"

using namespace Decent::DhtClient;

namespace
{
	jint ThrowNoClassDefFoundError(JNIEnv * env, const std::string & cName)
	{
		return env->ThrowNew(env->FindClass("java/lang/NoClassDefFoundError"), ("Class with name " + cName + "is not found!").c_str());
	}

	jint ThrowDhtClientBindingException(JNIEnv * env, const std::string & msg)
	{
		static constexpr char expName[] = "com/Decent/DhtClientBindingException";
		jclass expClass = env->FindClass(expName);

		return expClass ? env->ThrowNew(expClass, msg.c_str()) : ThrowNoClassDefFoundError(env, expName);
	}
}


JNIEXPORT void JNICALL Java_com_decent_dht_DhtClientBinding_init(JNIEnv * env, jclass)
{
	try
	{
		const DhtClientApp& decentapp = GetDhtClientApp();
	}
	catch (const std::exception& e)
	{
		ThrowDhtClientBindingException(env, std::string("Failed to initialize Decent DHT Client! Error Msg: ") + e.what());
		return;
	}
}

JNIEXPORT void JNICALL Java_com_decent_dht_DhtClientBinding_cleanup(JNIEnv * env, jclass)
{
	return;
}

JNIEXPORT jstring JNICALL Java_com_decent_dht_DhtClientBinding_read(JNIEnv * env, jclass, jstring key)
{
	const char * inCStr = env->GetStringUTFChars(key, NULL);
	if (inCStr == nullptr) { ThrowDhtClientBindingException(env, "Failed to retrieve Java String."); return nullptr; }
	std::string keyStr(inCStr);
	env->ReleaseStringUTFChars(key, inCStr);

	try
	{
		std::string val = GetDhtClientApp().Read(keyStr);

		return env->NewStringUTF(val.c_str());
	}
	catch (const std::exception& e)
	{
		ThrowDhtClientBindingException(env, std::string("Failed to read data! Error Msg: ") + e.what());
		return nullptr;
	}

}

JNIEXPORT void JNICALL Java_com_decent_dht_DhtClientBinding_insert(JNIEnv * env, jclass, jstring key, jstring val)
{
	const char * inCStr = env->GetStringUTFChars(key, NULL);
	if (inCStr == nullptr) { ThrowDhtClientBindingException(env, "Failed to retrieve Java String."); return; }
	std::string keyStr(inCStr);
	env->ReleaseStringUTFChars(key, inCStr);

	inCStr = env->GetStringUTFChars(val, NULL);
	if (inCStr == nullptr) { ThrowDhtClientBindingException(env, "Failed to retrieve Java String."); return; }
	std::string valStr(inCStr);
	env->ReleaseStringUTFChars(val, inCStr);

	try
	{
		GetDhtClientApp().Insert(keyStr, valStr);
	}
	catch (const std::exception& e)
	{
		ThrowDhtClientBindingException(env, std::string("Failed to insert data! Error Msg: ") + e.what());
	}
}

JNIEXPORT void JNICALL Java_com_decent_dht_DhtClientBinding_delete(JNIEnv * env, jclass, jstring key)
{
	const char * inCStr = env->GetStringUTFChars(key, NULL);
	if (inCStr == nullptr) { ThrowDhtClientBindingException(env, "Failed to retrieve Java String."); return; }
	std::string keyStr(inCStr);
	env->ReleaseStringUTFChars(key, inCStr);

	try
	{
		GetDhtClientApp().Delete(keyStr);
	}
	catch (const std::exception& e)
	{
		ThrowDhtClientBindingException(env, std::string("Failed to delete data! Error Msg: ") + e.what());
	}
}
