pidfile=/tmp/lock.pid
if [ -e $pidfile ]; then
    pid=`cat $pidfile`
    if kill -0 &>1 > /dev/null $pid; then
        echo "Already running"
        exit 0
    else
        rm $pidfile
    fi
fi
echo $$ > $pidfile

dbus-monitor --session "type='signal',interface='org.gnome.ScreenSaver'" |
  while read x; do
    case "$x" in 
      *"boolean true"*) ./off.sh;;
      *"boolean false"*) ./on.sh;;  
    esac
  done

rm $pidfile


