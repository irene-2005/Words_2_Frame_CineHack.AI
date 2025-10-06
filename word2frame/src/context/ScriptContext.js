import React, { createContext, useState, useEffect, useCallback, useMemo } from "react";

import {
  analyzeScript,
  createProject,
  fetchDefaultProject,
  fetchProjectSnapshot,
  uploadScript,
} from "../utils/apiClient";

export const ScriptContext = createContext();

const DEFAULT_PROJECT_ID = Number(process.env.REACT_APP_DEFAULT_PROJECT_ID || "0") || null;

const EMPTY_SCRIPT_DATA = {
  uploadedScript: null,
  sceneData: [],
  budget: { total: 0, perScene: [] },
  scheduleData: [],
  crew: [],
  actors: [],
  reports: null,
  productionBoard: {},
};

const useToast = () =>
  useCallback((message) => {
    if (!message) return;
    if (typeof window !== "undefined" && typeof window.showSiteToast === "function") {
      window.showSiteToast(message);
    } else {
      // eslint-disable-next-line no-console
      console.warn(message);
    }
  }, []);

export const ScriptProvider = ({ children, session }) => {
  const [scriptData, setScriptData] = useState(EMPTY_SCRIPT_DATA);
  const [project, setProject] = useState(null);
  const [projectId, setProjectId] = useState(DEFAULT_PROJECT_ID);
  const [analysisStatus, setAnalysisStatus] = useState("idle");
  const [statusMessage, setStatusMessage] = useState("");
  const [isLoadingSnapshot, setIsLoadingSnapshot] = useState(false);
  const [isCreatingProject, setIsCreatingProject] = useState(false);
  const [lastAnalyzedFilename, setLastAnalyzedFilename] = useState(null);

  const showToast = useToast();
  const authToken = session?.access_token || null;

  const normaliseSnapshot = useCallback((snapshot) => {
    if (!snapshot || !snapshot.project) {
      return {
        project: null,
        scriptData: { ...EMPTY_SCRIPT_DATA },
      };
    }

    const script = snapshot.scriptData || {};
    const sceneData = (script.sceneData || []).map((scene) => ({
      id: scene.id,
      index: scene.index,
      scene: scene.scene || scene.heading || `Scene ${scene.index}`,
      location: scene.location || "Unknown",
      type: scene.type || null,
      summary: scene.summary || "",
      wordCount: scene.wordCount || 0,
      predictedBudget: Number(scene.predictedBudget || 0),
      suggestedLocation: scene.suggestedLocation || scene.location || null,
      progressStatus: scene.progressStatus || "todo",
      characters: new Set(scene.characters || []),
      props: new Set(scene.props || []),
    }));

    const budget = {
      total: Number(script.budget?.total || 0),
      perScene: (script.budget?.perScene || []).map((entry) => ({
        scene: entry.scene,
        total: Number(entry.total || 0),
      })),
    };

    const scheduleData = (script.scheduleData || []).map((entry, index) => ({
      id: entry.id ?? index,
      date: entry.date,
      scene: entry.scene,
      location: entry.location || "TBD",
      cast: Array.isArray(entry.cast) ? entry.cast : [],
    }));

    const crew = (script.crew || []).map((member, index) => ({
      id: member.id ?? index,
      name: member.name,
      role: member.role,
    }));

    const actors = (script.actors || []).map((actor, index) => ({
      id: actor.id ?? `actor-${index}`,
      name: actor.name,
      role: actor.role || "Cast",
      cost: actor.cost,
    }));

    const productionBoard = Object.entries(script.productionBoard || {}).reduce(
      (acc, [column, tasks]) => {
        acc[column] = (tasks || []).map((task, index) => ({
          id: task.id ?? `${column}-${index}`,
          title: task.title,
          scene: task.scene,
          status: task.status || "todo",
          assignedTo: task.assignedTo || "Unassigned",
        }));
        return acc;
      },
      {}
    );

    return {
      project: snapshot.project,
      scriptData: {
        uploadedScript: script.uploadedScript || null,
        sceneData,
        budget,
        scheduleData,
        crew,
        actors,
        reports: script.reports || null,
        productionBoard,
      },
    };
  }, []);

  const applySnapshot = useCallback((payload) => {
    setProject(payload.project);
    setScriptData(payload.scriptData);
    const uploadedName = payload?.scriptData?.uploadedScript?.name || null;
    setLastAnalyzedFilename(uploadedName);
  }, []);

  const refreshSnapshot = useCallback(
    async (overrideProjectId) => {
      const targetId = overrideProjectId || projectId;
      if (!authToken || !targetId) {
        return null;
      }
      setIsLoadingSnapshot(true);
      try {
        const snapshot = await fetchProjectSnapshot(targetId, authToken);
        const normalised = normaliseSnapshot(snapshot);
        applySnapshot(normalised);
        if (snapshot?.project) {
          setProject(snapshot.project);
        }
        if (targetId !== projectId) {
          setProjectId(targetId);
        }
        return normalised;
      } catch (error) {
        showToast(error.message || "Unable to load project snapshot");
        throw error;
      } finally {
        setIsLoadingSnapshot(false);
      }
    },
    [authToken, projectId, normaliseSnapshot, applySnapshot, showToast]
  );

  const resolveProject = useCallback(async () => {
    if (!authToken) {
      return null;
    }
    try {
      const projectResponse = await fetchDefaultProject(authToken);
      if (projectResponse?.id) {
        setProjectId(projectResponse.id);
        setProject(projectResponse);
        return projectResponse.id;
      }
    } catch (error) {
      showToast(error.message || "Unable to resolve default project");
    }
    if (DEFAULT_PROJECT_ID) {
      setProjectId(DEFAULT_PROJECT_ID);
      return DEFAULT_PROJECT_ID;
    }
    return null;
  }, [authToken, showToast]);

  useEffect(() => {
    let cancelled = false;

    if (!authToken) {
      setScriptData(EMPTY_SCRIPT_DATA);
      setProject(null);
      setProjectId(DEFAULT_PROJECT_ID);
      setAnalysisStatus("idle");
      setStatusMessage("");
      setLastAnalyzedFilename(null);
      return () => {
        cancelled = true;
      };
    }

    (async () => {
      const id = await resolveProject();
      if (cancelled) return;
      const target = id || projectId;
      if (target) {
        try {
          await refreshSnapshot(target);
        } catch (error) {
          // eslint-disable-next-line no-console
          console.error("Snapshot refresh failed", error);
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [authToken, projectId, resolveProject, refreshSnapshot]);

  const uploadAndAnalyze = useCallback(
    async (file) => {
      if (!authToken) {
        throw new Error("You must be signed in to upload a script");
      }
      const targetProjectId = projectId || (await resolveProject());
      if (!targetProjectId) {
        throw new Error("No project available for script analysis");
      }

      setAnalysisStatus("uploading");
      setStatusMessage("Uploading script to Words2Frame...");
      setScriptData((prev) => ({
        ...prev,
        uploadedScript: {
          name: file?.name || prev.uploadedScript?.name || "Uploaded Script",
          status: "Processing",
        },
      }));

      try {
        const uploadResult = await uploadScript(targetProjectId, file, authToken);
        setLastAnalyzedFilename(uploadResult?.filename || null);
        setAnalysisStatus("analyzing");
        setStatusMessage("Analyzing script with AI — sit tight...");

        const analysisResult = await analyzeScript(targetProjectId, uploadResult.filename, authToken);
        const snapshot = analysisResult?.snapshot;
        if (snapshot) {
          const normalised = normaliseSnapshot(snapshot);
          applySnapshot(normalised);
          setProject(snapshot.project || null);
        } else {
          await refreshSnapshot(targetProjectId);
        }

        setAnalysisStatus("completed");
        setStatusMessage("Analysis complete! Dashboard updated.");
        showToast("Script analysis finished successfully.");
      } catch (error) {
        setAnalysisStatus("error");
        const message = error.message || "Script analysis failed.";
        setStatusMessage(message);
        showToast(message);
        throw error;
      }
    },
    [authToken, projectId, resolveProject, normaliseSnapshot, applySnapshot, refreshSnapshot, showToast]
  );

  const runScriptBreakdown = useCallback(async () => {
    if (!authToken) {
      throw new Error("You must be signed in to analyze a script");
    }
    const targetProjectId = projectId || (await resolveProject());
    if (!targetProjectId) {
      throw new Error("No project available for script analysis");
    }
    const filename = lastAnalyzedFilename || scriptData?.uploadedScript?.name;
    if (!filename) {
      throw new Error("Upload a script before running the analysis");
    }

    setAnalysisStatus("analyzing");
    setStatusMessage("Crunching your script with AI...");
    try {
      const result = await analyzeScript(targetProjectId, filename, authToken);
      const snapshot = result?.snapshot;
      if (snapshot) {
        const normalised = normaliseSnapshot(snapshot);
        applySnapshot(normalised);
        setProject(snapshot.project || null);
      } else {
        await refreshSnapshot(targetProjectId);
      }
      setLastAnalyzedFilename(filename);
      setAnalysisStatus("completed");
      setStatusMessage("Fresh breakdown ready!");
      showToast("Script breakdown updated.");
    } catch (error) {
      setAnalysisStatus("error");
      const message = error.message || "Script breakdown failed.";
      setStatusMessage(message);
      showToast(message);
      throw error;
    }
  }, [
    authToken,
    projectId,
    resolveProject,
    lastAnalyzedFilename,
    scriptData,
    normaliseSnapshot,
    applySnapshot,
    refreshSnapshot,
    showToast,
  ]);

  const createNewProject = useCallback(
    async (overrides = {}) => {
      if (!authToken) {
        throw new Error("You must be signed in to create a project");
      }
      setIsCreatingProject(true);
      try {
        const now = new Date();
        const fallbackName = `Untitled Project ${now.toLocaleDateString()} ${now.toLocaleTimeString()}`;
        const payload = {
          name: overrides.name || fallbackName,
          description: overrides.description || "Auto-generated workspace",
          budget: overrides.budget ?? 750000,
        };
        const created = await createProject(payload, authToken);
        setProject(created);
        setProjectId(created.id);
        setScriptData(EMPTY_SCRIPT_DATA);
        setAnalysisStatus("idle");
        setStatusMessage("");
        setLastAnalyzedFilename(null);
        showToast("New project ready. Upload a script to begin.");
        await refreshSnapshot(created.id);
        return created;
      } catch (error) {
        showToast(error.message || "Unable to create project");
        throw error;
      } finally {
        setIsCreatingProject(false);
      }
    },
    [authToken, refreshSnapshot, showToast]
  );

  const contextValue = useMemo(
    () => ({
      scriptData,
      setScriptData,
      project,
      projectId,
      refreshSnapshot,
      uploadAndAnalyze,
      runScriptBreakdown,
      createNewProject,
      analysisStatus,
      statusMessage,
      isLoadingSnapshot,
      isCreatingProject,
      authToken,
    }),
    [
      scriptData,
      project,
      projectId,
      refreshSnapshot,
      uploadAndAnalyze,
      runScriptBreakdown,
      createNewProject,
      analysisStatus,
      statusMessage,
      isLoadingSnapshot,
      isCreatingProject,
      authToken,
    ]
  );

  return <ScriptContext.Provider value={contextValue}>{children}</ScriptContext.Provider>;
};