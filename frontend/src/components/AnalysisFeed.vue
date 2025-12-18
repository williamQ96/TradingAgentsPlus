<script setup>
import { computed, ref, watch, nextTick } from 'vue';
import { LineChart, Users, Newspaper, FileText, Search, Cpu, ChevronDown, ChevronUp, Loader2 } from 'lucide-vue-next';

const props = defineProps({
  events: {
    type: Array,
    required: true
  },
  status: {
    type: String,
    required: true
  },
  selectedNodeId: {
    type: String,
    default: null
  }
});

const emit = defineEmits(['select-report']);

const feedContainer = ref(null);
const expandedNodes = ref(new Set());

// Auto-scroll to bottom when new events arrive
watch(() => props.events.length, async () => {
  await nextTick();
  if (feedContainer.value) {
    feedContainer.value.scrollTop = feedContainer.value.scrollHeight;
  }
});

const formatTime = (isoString) => {
  if (!isoString) return '';
  return new Date(isoString).toLocaleTimeString();
};

const formatNodeName = (name) => {
    if (!name) return 'System';
    if (name === 'System') return 'System';
    return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const getAgentIcon = (name) => {
    if (!name) return Cpu;
    const n = name.toLowerCase();
    if (n.includes('market')) return LineChart;
    if (n.includes('social')) return Users;
    if (n.includes('news')) return Newspaper;
    if (n.includes('fundamental')) return FileText;
    return Search;
};

const toggleExpand = (nodeName) => {
    if (expandedNodes.value.has(nodeName)) {
        expandedNodes.value.delete(nodeName);
    } else {
        expandedNodes.value.add(nodeName);
    }
};

const handleReportClick = (event) => {
    if (event.displayContent || event.type === 'report') {
        emit('select-report', event);
    }
};
</script>

<template>
  <div class="h-full flex flex-col bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
    <div ref="feedContainer" class="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
      
      <div v-if="events.length === 0" class="h-full flex flex-col items-center justify-center text-gray-400">
        <span v-if="status === 'idle'">Ready to start analysis</span>
        <span v-else-if="status === 'running'" class="animate-pulse">Waiting for events...</span>
      </div>

      <div 
        v-for="(event, index) in events" 
        :key="event.nodeName"
        class="border border-gray-100 rounded-lg bg-white overflow-hidden transition-all duration-200"
        :class="[
            selectedNodeId === event.nodeName ? 'ring-2 ring-emerald-500 shadow-md' : 'shadow-sm hover:shadow-md'
        ]"
      >
        <!-- Header: Always Visible -->
        <div @click="toggleExpand(event.nodeName)" class="flex items-center justify-between p-3 bg-gray-50/50 cursor-pointer hover:bg-gray-100 transition-colors">
           <div class="flex items-center gap-3">
               <div class="p-1.5 bg-white rounded-md border border-gray-200 shadow-sm text-emerald-600">
                   <component :is="getAgentIcon(event.nodeName)" class="w-4 h-4" />
               </div>
               <div>
                   <div class="font-bold text-gray-700 font-mono text-xs uppercase tracking-tight">{{ formatNodeName(event.nodeName) }}</div>
                   <div class="text-[10px] text-gray-400 font-medium">{{ formatTime(event.timestamp) }}</div>
               </div>
           </div>
           
           <button class="text-gray-400 hover:text-gray-600">
               <ChevronUp v-if="expandedNodes.has(event.nodeName)" class="w-4 h-4" />
               <ChevronDown v-else class="w-4 h-4" />
           </button>
        </div>
        
        <!-- Body: Collapsible -->
        <div v-if="expandedNodes.has(event.nodeName)" class="p-3 border-t border-gray-100 bg-white animate-in slide-in-from-top-2 duration-200">
           <div class="text-gray-800 leading-relaxed text-xs">
               <!-- Content Present -->
               <template v-if="event.displayContent">
                   <button 
                      v-if="event.type === 'report'" 
                      @click.stop="handleReportClick(event)"
                      class="w-full mb-2 flex items-center justify-center gap-2 py-1.5 px-3 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-semibold rounded-md border border-emerald-200 transition-colors text-xs"
                   >
                       <FileText class="w-3.5 h-3.5" /> View Generated Report
                   </button>
                   
                   <div v-else class="whitespace-pre-wrap font-mono bg-gray-50 p-2 rounded border border-gray-100 text-gray-600">
                     {{ event.displayContent }}
                   </div>
               </template>

               <!-- No Content: Loading or Completed -->
               <template v-else>
                   <div v-if="status !== 'complete'" class="flex items-center gap-2 text-emerald-600 py-2">
                     <Loader2 class="w-4 h-4 animate-spin" />
                     <span class="text-xs font-medium animate-pulse">Processing Agent Data...</span>
                   </div>
                   <div v-else class="text-gray-400 italic flex items-center gap-2 py-2">
                       <div class="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
                       <span>Completed</span>
                   </div>
               </template>
            </div>
        </div>

      </div>

    </div>
  </div>
</template>
