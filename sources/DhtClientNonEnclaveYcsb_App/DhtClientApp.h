#pragma once

#include <memory>
#include <string>

namespace Decent
{
	namespace DhtClient
	{
		class ConnectionPool;

		class DhtClientApp
		{
		public:
			DhtClientApp() = default;

			virtual ~DhtClientApp();

			void Init();

			virtual void Insert(std::shared_ptr<ConnectionPool> cntPool, const std::string& key, const std::string& val);

			virtual std::string Read(std::shared_ptr<ConnectionPool> cntPool, const std::string& key);

			virtual void Delete(std::shared_ptr<ConnectionPool> cntPool, const std::string& key);

		private:
		};
	}
}

