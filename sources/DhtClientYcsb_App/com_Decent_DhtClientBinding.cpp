#include "../DhtClientYcsb_Java/com_Decent_DhtClientBinding.h"

#include <string>

#include <boost/filesystem.hpp>

#include <DecentApi/Common/Ra/WhiteList/WhiteList.h>

#include <DecentApi/CommonApp/Ra/Messages.h>
#include <DecentApi/CommonApp/Tools/DiskFile.h>
#include <DecentApi/CommonApp/Tools/ConfigManager.h>
#include <DecentApi/CommonApp/Net/TCPConnection.h>

#include "ConnectionManager.h"
#include "DhtClientApp.h"

using namespace Decent::Tools;
using namespace Decent::Ra;
using namespace Decent::Net;
using namespace Decent::DhtClient;

namespace
{
	constexpr char gsk_configFilePaht[] = "Config.json";
	constexpr char gsk_whiteListKey[] = "DhtTestClientWhiteList";

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

	std::string GetConfigJsonStr()
	{
		DiskFile file(gsk_configFilePaht, FileBase::Mode::Read);

		std::string res;
		res.resize(file.GetFileSize());
		file.ReadBlockExactSize(res);

		return res;
	}

	const ConfigManager& GetConfigManager()
	{
		static ConfigManager configManager(GetConfigJsonStr());

		return configManager;
	}

	const ConfigItem& GetDecentServerItem()
	{
		static const ConfigItem& decentServerItem = GetConfigManager().GetItem(WhiteList::sk_nameDecentServer);
		return decentServerItem;
	}

	std::unique_ptr<Connection> GetDecentServerConnection()
	{
		static uint32_t serverIp = TCPConnection::GetIpAddressFromStr(GetDecentServerItem().GetAddr());
		return std::make_unique<TCPConnection>(serverIp, GetDecentServerItem().GetPort());
	}

	std::unique_ptr<Connection> SendWhiteListAndGetDecentServerConnection()
	{
		GetDecentServerConnection()->SendPack(Message::LoadWhiteList(gsk_whiteListKey, GetConfigManager().GetLoadedWhiteListStr()));
		return GetDecentServerConnection();
	}

	DhtClientApp& GetDhtClientApp()
	{
		static DhtClientApp inst(ENCLAVE_FILENAME, KnownFolderType::LocalAppDataEnclave, TOKEN_FILENAME, gsk_whiteListKey, *SendWhiteListAndGetDecentServerConnection());

		return inst;
	}
}


JNIEXPORT void JNICALL Java_com_Decent_DhtClientBinding_init(JNIEnv * env, jclass)
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

JNIEXPORT void JNICALL Java_com_Decent_DhtClientBinding_cleanup(JNIEnv * env, jclass)
{
	return;
}

JNIEXPORT jstring JNICALL Java_com_Decent_DhtClientBinding_read(JNIEnv * env, jclass, jstring key)
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

JNIEXPORT void JNICALL Java_com_Decent_DhtClientBinding_insert(JNIEnv * env, jclass, jstring key, jstring val)
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

JNIEXPORT void JNICALL Java_com_Decent_DhtClientBinding_delete(JNIEnv * env, jclass, jstring key)
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
