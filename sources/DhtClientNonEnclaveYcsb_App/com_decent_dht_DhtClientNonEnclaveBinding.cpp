#include "../DhtClientYcsb_Java/com_decent_dht_DhtClientNonEnclaveBinding.h"

#include <string>

#include <DecentApi/Common/Common.h>

#include "DhtClientApp.h"
#include "EnclaveInitializer.h"
#include "DhtClientAppPkg.h"

using namespace Decent::DhtClient;

namespace
{
	jint ThrowNoClassDefFoundError(JNIEnv * env, const std::string & cName)
	{
		return env->ThrowNew(env->FindClass("java/lang/NoClassDefFoundError"), ("Class with name " + cName + "is not found!").c_str());
	}

	jint ThrowDhtClientBindingException(JNIEnv * env, const std::string & msg)
	{
		static constexpr char expName[] = "com/decent/dht/DhtClientBindingException";
		jclass expClass = env->FindClass(expName);

		return expClass ? env->ThrowNew(expClass, msg.c_str()) : ThrowNoClassDefFoundError(env, expName);
	}

	void* Long2Ptr(jlong v)
	{
		return reinterpret_cast<void*>(v);
	}

	jlong Ptr2Long(void* ptr)
	{
		return reinterpret_cast<jlong>(ptr);
	}

	static jclass gsk_bindingClass = nullptr;
	static jfieldID gsk_bindingClassCPtr = nullptr;
}

JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM* vm, void* reserved)
{
	JNIEnv* env;
	if (vm->GetEnv(reinterpret_cast<void**>(&env), JNI_VERSION_10) != JNI_OK)
	{
		return JNI_ERR;
	}

	jclass tmpbindingClass = env->FindClass("com/decent/dht/DhtClientNonEnclaveBinding");

	gsk_bindingClass = reinterpret_cast<jclass>(env->NewGlobalRef(tmpbindingClass));
	if (gsk_bindingClass == nullptr)
	{
		return JNI_ERR;
	}

	env->DeleteLocalRef(tmpbindingClass);

	gsk_bindingClassCPtr = env->GetFieldID(gsk_bindingClass, "cPtr", "J");
	if (gsk_bindingClassCPtr == nullptr)
	{
		return JNI_ERR;
	}

	return JNI_VERSION_10;
}

JNIEXPORT void JNICALL JNI_OnUnload(JavaVM *vm, void *reserved)
{
	JNIEnv* env;
	vm->GetEnv(reinterpret_cast<void**>(&env), JNI_VERSION_10);

	env->DeleteGlobalRef(gsk_bindingClass);
}

JNIEXPORT void JNICALL Java_com_decent_dht_DhtClientNonEnclaveBinding_init(JNIEnv * env, jobject obj, jlong maxOpPerTicket)
{
	try
	{
		DhtClientAppPkg* decentappPkg = GetNewDhtClientAppPkg(100, static_cast<int64_t>(maxOpPerTicket));
		env->SetLongField(obj, gsk_bindingClassCPtr, Ptr2Long(decentappPkg));
	}
	catch (const std::exception& e)
	{
		ThrowDhtClientBindingException(env, std::string("Failed to initialize Decent DHT Client! Error Msg: ") + e.what());
		return;
	}
}

JNIEXPORT void JNICALL Java_com_decent_dht_DhtClientNonEnclaveBinding_cleanup(JNIEnv * env, jobject obj)
{
	jlong cPtr = env->GetLongField(obj, gsk_bindingClassCPtr);

	delete static_cast<DhtClientAppPkg*>(Long2Ptr(cPtr));

	return;
}

JNIEXPORT jstring JNICALL Java_com_decent_dht_DhtClientNonEnclaveBinding_read(JNIEnv * env, jobject obj, jstring key)
{
	jlong cPtr = env->GetLongField(obj, gsk_bindingClassCPtr);
	if(Long2Ptr(cPtr) == nullptr) { ThrowDhtClientBindingException(env, "Please Initialize first!"); return nullptr; }
	DhtClientAppPkg& decentappPkg = *static_cast<DhtClientAppPkg*>(Long2Ptr(cPtr));

	const char * inCStr = env->GetStringUTFChars(key, NULL);
	if (inCStr == nullptr) { ThrowDhtClientBindingException(env, "Failed to retrieve Java String."); return nullptr; }
	std::string keyStr(inCStr);
	env->ReleaseStringUTFChars(key, inCStr);

	try
	{
		std::string val = decentappPkg.m_app->Read(decentappPkg.m_cntPool, keyStr);

		return env->NewStringUTF(val.c_str());
	}
	catch (const std::exception& e)
	{
		ThrowDhtClientBindingException(env, std::string("Failed to read data! Error Msg: ") + e.what());
		return nullptr;
	}

}

JNIEXPORT void JNICALL Java_com_decent_dht_DhtClientNonEnclaveBinding_insert(JNIEnv * env, jobject obj, jstring key, jstring val)
{
	jlong cPtr = env->GetLongField(obj, gsk_bindingClassCPtr);
	if (Long2Ptr(cPtr) == nullptr) { ThrowDhtClientBindingException(env, "Please Initialize first!"); return; }
	DhtClientAppPkg& decentappPkg = *static_cast<DhtClientAppPkg*>(Long2Ptr(cPtr));

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
		decentappPkg.m_app->Insert(decentappPkg.m_cntPool, keyStr, valStr);
	}
	catch (const std::exception& e)
	{
		ThrowDhtClientBindingException(env, std::string("Failed to insert data! Error Msg: ") + e.what());
	}
}

JNIEXPORT void JNICALL Java_com_decent_dht_DhtClientNonEnclaveBinding_update(JNIEnv * env, jobject obj, jstring key, jstring val)
{
	jlong cPtr = env->GetLongField(obj, gsk_bindingClassCPtr);
	if (Long2Ptr(cPtr) == nullptr) { ThrowDhtClientBindingException(env, "Please Initialize first!"); return; }
	DhtClientAppPkg& decentappPkg = *static_cast<DhtClientAppPkg*>(Long2Ptr(cPtr));

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
		decentappPkg.m_app->Update(decentappPkg.m_cntPool, keyStr, valStr);
	}
	catch (const std::exception& e)
	{
		ThrowDhtClientBindingException(env, std::string("Failed to insert data! Error Msg: ") + e.what());
	}
}

JNIEXPORT void JNICALL Java_com_decent_dht_DhtClientNonEnclaveBinding_delete(JNIEnv * env, jobject obj, jstring key)
{
	jlong cPtr = env->GetLongField(obj, gsk_bindingClassCPtr);
	if (Long2Ptr(cPtr) == nullptr) { ThrowDhtClientBindingException(env, "Please Initialize first!"); return; }
	DhtClientAppPkg& decentappPkg = *static_cast<DhtClientAppPkg*>(Long2Ptr(cPtr));

	const char * inCStr = env->GetStringUTFChars(key, NULL);
	if (inCStr == nullptr) { ThrowDhtClientBindingException(env, "Failed to retrieve Java String."); return; }
	std::string keyStr(inCStr);
	env->ReleaseStringUTFChars(key, inCStr);

	try
	{
		decentappPkg.m_app->Delete(decentappPkg.m_cntPool, keyStr);
	}
	catch (const std::exception& e)
	{
		ThrowDhtClientBindingException(env, std::string("Failed to delete data! Error Msg: ") + e.what());
	}
}
