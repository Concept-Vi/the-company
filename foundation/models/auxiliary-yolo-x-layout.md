---
type: model
id: unstructuredio/yolo_x_layout
filename: auxiliary-yolo-x-layout
status: auxiliary
runtime: not-yet-served
date_added: present-before-substrate-setup
tags: [foundation, models, layout, auxiliary, multimodal-pipeline]
---

# YOLO X Layout (auxiliary)

> [[_models-index|← Models hub]] · auxiliary; document layout detector

## At a glance

| Field | Value |
|---|---|
| HF id | `unstructuredio/yolo_x_layout` |
| Disk | 207 MB |
| Architecture | YOLO X object detector, trained for document layout detection |
| Status | present on disk; used by document-processing tooling |

## Source

Present in the HF cache prior to deliberate substrate setup. Part of `unstructured.io`'s document-processing pipeline — detects document regions (text blocks, tables, figures, headers, footers) in scanned or rasterised PDFs as a preprocessing step before embedding or extraction.

## Fits these needs

- [[_models-index#Multimodal: text + image + visual documents (charts, PDFs with layout)|Multimodal: text + image + visual documents]] — sits *upstream* of the multimodal embedder in a typical doc-RAG pipeline (detect regions → crop → embed each region appropriately).

## Open at this entry

- Whether `unstructured.io` is the document pipeline Tim's work uses, or whether this is a one-off auto-download
- Whether to register a "Document layout / preprocessing" need-category at the hub level
- The full doc-RAG pipeline using this + [[jina-embeddings-v4]] never assembled end-to-end on this substrate

## Connects to

- [[_models-index]] — hub
- [[jina-embeddings-v4]] — likely downstream consumer
