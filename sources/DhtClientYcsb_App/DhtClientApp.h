#pragma once

#include <DecentApi/DecentAppApp/DecentApp.h>

namespace Decent
{
	namespace DhtClient
	{
		class ConnectionPool;

		class DhtClientApp : public Decent::RaSgx::DecentApp
		{
		public:
			using DecentApp::DecentApp;

			virtual ~DhtClientApp();

			void Init(std::shared_ptr<ConnectionPool> cntPool);

			virtual void Insert(const std::string& key, const std::string& val);

			virtual std::string Read(const std::string& key);

			virtual void Delete(const std::string& key);

			virtual bool ProcessSmartMessage(const std::string& category, Net::ConnectionBase& connection, Net::ConnectionBase*& freeHeldCnt) override;

		private:
		};
	}
}

