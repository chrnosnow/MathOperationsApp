#!/bin/bash
set -e

host=$1
shift
cmd="$@"

until nc -z $(echo $host | cut -d: -f1) $(echo $host | cut -d: -f2); do
  >&2 echo "Kafka ($host) is unavailable - sleeping"
  sleep 1
done

>&2 echo "Kafka ($host) is up - executing command"
exec $cmd