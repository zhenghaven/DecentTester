#include <DecentApi/DecentAppEnclave/AppStates.h>
#include <DecentApi/DecentAppEnclave/AppStatesSingleton.h>
#include <DecentApi/Common/Ra/StatesSingleton.h>

#include <DecentApi/DecentAppEnclave/AppCertContainer.h>
#include <DecentApi/Common/Ra/KeyContainer.h>
#include <DecentApi/Common/Ra/WhiteList/LoadedList.h>
#include <DecentApi/Common/Ra/WhiteList/DecentServer.h>

#include "ConnectionManager.h"
#include "StatesSingleton.h"

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

	static const WhiteList::LoadedList& GetLoadedWhiteListImpl(WhiteList::LoadedList* instPtr)
	{
		static const WhiteList::LoadedList inst(instPtr);
		return inst;
	}

	static ConnectionManager& GetConnectionMgr()
	{
		static ConnectionManager inst(50, 10);
		return inst;
	}
}

DhtClient::States& DhtClient::GetStatesSingleton()
{
	static States state(GetCertContainer(), GetKeyContainer(), GetServerWhiteList(), &GetLoadedWhiteListImpl, GetConnectionMgr());

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
