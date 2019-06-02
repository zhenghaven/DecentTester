#include <string>
#include <memory>
#include <iostream>

#include "DhtClientApp.h"
#include "EnclaveInitializer.h"
#include "DhtClientAppPkg.h"

using namespace Decent::DhtClient;

int main(int argc, char ** argv)
{
	try
	{
		std::unique_ptr<DhtClientAppPkg> dhtClientAppPkg(GetNewDhtClientAppPkg(100));
		dhtClientAppPkg->m_app->Insert(dhtClientAppPkg->m_cntPool, "TestKey1", "TestVal1");
		dhtClientAppPkg->m_app->Insert(dhtClientAppPkg->m_cntPool, "TestKey2", "TestVal2");
		dhtClientAppPkg->m_app->Insert(dhtClientAppPkg->m_cntPool, "TestKey3", "TestVal3");
		dhtClientAppPkg->m_app->Insert(dhtClientAppPkg->m_cntPool, "TestKey4", "TestVal4");
		dhtClientAppPkg->m_app->Insert(dhtClientAppPkg->m_cntPool, "TestKey5", "TestVal5");

		std::string readRes1 = dhtClientAppPkg->m_app->Read(dhtClientAppPkg->m_cntPool, "TestKey1");
		std::string readRes2 = dhtClientAppPkg->m_app->Read(dhtClientAppPkg->m_cntPool, "TestKey2");
		std::string readRes3 = dhtClientAppPkg->m_app->Read(dhtClientAppPkg->m_cntPool, "TestKey3");
		std::string readRes4 = dhtClientAppPkg->m_app->Read(dhtClientAppPkg->m_cntPool, "TestKey4");
		std::string readRes5 = dhtClientAppPkg->m_app->Read(dhtClientAppPkg->m_cntPool, "TestKey5");
	}
	catch (const std::exception& e)
	{
		std::cout << "Caught exception: " << e.what();
	}

	return 0;
}