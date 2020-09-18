#!/bin/bash

user_name=root
if [ $EXEC_USER_ID ];
then
  if ! id $EXEC_USER_ID;then
    useradd  -u $EXEC_USER_ID wild
  fi
  user_name=wild
fi
runuser  $user_name -c "$*"
