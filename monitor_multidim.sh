#!/bin/bash
# Monitor multi-dimensional fairness run progress

LOG_FILE="multidim_run.log"
RESULTS_FILE="data/summary_multidim_3d_full.csv"

echo "=========================================="
echo "MULTI-DIMENSIONAL FAIRNESS RUN MONITOR"
echo "=========================================="
echo ""

# Check if processes are running
echo "📊 Process Status:"
if ps aux | grep -q "[r]un_multidim_sweep"; then
    echo "  ✅ Processes running"
    ps aux | grep "[r]un_multidim_sweep" | grep -v grep | awk '{print "    PID: " $2 ", Runtime: " $10 ", CPU: " $3 "%"}'
else
    echo "  ⏹️  No processes found"
fi
echo ""

# Check log file
echo "📋 Log File Status:"
if [ -f "$LOG_FILE" ]; then
    SIZE=$(ls -lh "$LOG_FILE" | awk '{print $5}')
    LINES=$(wc -l < "$LOG_FILE" 2>/dev/null || echo "0")
    echo "  File: $LOG_FILE"
    echo "  Size: $SIZE"
    echo "  Lines: $LINES"
    if [ "$LINES" -gt 0 ]; then
        echo ""
        echo "  Last 10 lines:"
        echo "  ---"
        tail -10 "$LOG_FILE" | sed 's/^/  /'
    else
        echo "  (Empty - output may be buffered)"
    fi
else
    echo "  ⏳ Log file not found"
fi
echo ""

# Check results file
echo "📁 Results File Status:"
if [ -f "$RESULTS_FILE" ]; then
    SIZE=$(ls -lh "$RESULTS_FILE" | awk '{print $5}')
    echo "  ✅ File exists: $RESULTS_FILE"
    echo "  Size: $SIZE"
    echo ""
    echo "  Results preview:"
    echo "  ---"
    head -5 "$RESULTS_FILE" | sed 's/^/  /'
    echo ""
    echo "  ✅ RUN COMPLETE!"
else
    echo "  ⏳ Results file not created yet"
    echo "  (Will appear when all 8 configurations finish)"
fi
echo ""

# Check for errors
if [ -f "$LOG_FILE" ] && [ -s "$LOG_FILE" ]; then
    ERROR_COUNT=$(grep -i "error\|exception\|traceback\|failed" "$LOG_FILE" | wc -l | tr -d ' ')
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo "⚠️  Errors found in log:"
        grep -i "error\|exception\|traceback\|failed" "$LOG_FILE" | head -5 | sed 's/^/  /'
        echo ""
    fi
fi

echo "=========================================="
echo "Run this script again to check progress:"
echo "  ./monitor_multidim.sh"
echo ""
echo "Or watch live:"
echo "  watch -n 10 ./monitor_multidim.sh"
echo "=========================================="

