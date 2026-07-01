// TaskTree.jsx — Vi's three-layer agent visualisation
function TaskNode({ name, meta, state }) {
  return (
    <div className={`vi-node ${state}`}>
      <div className="top">
        <span className="dot"></span>
        <span className="name">{name}</span>
      </div>
      {meta && <span className="meta">{meta}</span>}
    </div>
  );
}

function TaskTree({ layers }) {
  return (
    <div className="vi-tasks">
      {layers.map((layer, i) => (
        <React.Fragment key={i}>
          <div className={`vi-layer layer-${i+1}`}>
            <div className="vi-layer-head">
              <span className="vi-layer-tag">Layer {i+1}</span>
              <span className="vi-layer-desc">{layer.desc}</span>
            </div>
            <div className="vi-layer-nodes">
              {layer.nodes.map((n, j) => <TaskNode key={j} {...n}/>)}
            </div>
          </div>
          {i < layers.length - 1 && <div className="vi-layer-connector"/>}
        </React.Fragment>
      ))}
    </div>
  );
}

window.TaskTree = TaskTree;
