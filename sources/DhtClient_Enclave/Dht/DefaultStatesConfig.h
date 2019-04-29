#include <DecentApi/DecentAppEnclave/AppStates.h>
#include <DecentApi/DecentAppEnclave/AppStatesSingleton.h>
#include <DecentApi/Common/Ra/StatesSingleton.h>

#include <DecentApi/DecentAppEnclave/AppCertContainer.h>
#include <DecentApi/Common/Ra/KeyContainer.h>
#include <DecentApi/Common/Ra/WhiteList/Loaded.h>
#include <DecentApi/Common/Ra/WhiteList/DecentServer.h>

#include "DhtClientConnectionPool.h"
#include "DhtClientStatesSingleton.h"

using namespace Decent;
using namespace Decent::Ra;
using namespace Decent::DhtClient;

namespace
{
	static AppCertContainer& GetCertContainer()
	{
		static AppCertContainer inst;
		return inst;
	}

	static KeyContainer& GetKeyContainer()
	{
		static KeyContainer inst;
		return inst;
	}

	static WhiteList::DecentServer& GetServerWhiteList()
	{
		static WhiteList::DecentServer inst;
		return inst;
	}

	static const WhiteList::Loaded& GetLoadedWhiteListImpl(WhiteList::Loaded* instPtr)
	{
		static const WhiteList::Loaded inst(instPtr);
		return inst;
	}

	static ConnectionPool& GetConnectionPool()
	{
		static ConnectionPool inst(5, 5);
		return inst;
	}
}

DhtClient::States& DhtClient::GetStatesSingleton()
{
	static States state(GetCertContainer(), GetKeyContainer(), GetServerWhiteList(), &GetLoadedWhiteListImpl, GetConnectionPool());

	return state;
}

AppStates& Decent::Ra::GetAppStateSingleton()
{
	return GetStatesSingleton();
}

Ra::States& Decent::Ra::GetStateSingleton()
{
	return GetAppStateSingleton();
}
