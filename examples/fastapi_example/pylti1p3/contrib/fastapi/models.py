from typing import List, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl


class LTIKey(BaseModel):
    """LTI Key model."""
    kid: str = Field(..., description="Key ID")
    alg: str = Field(..., description="Algorithm")


class LTIKeySet(BaseModel):
    """LTI Key Set model."""
    keys: List[LTIKey] = Field(..., description="List of keys")


class LTIResourceLink(BaseModel):
    """LTI Resource Link claim model."""
    id: str = Field(..., description="Resource link ID")
    description: Optional[str] = Field(None, description="Resource description")
    title: Optional[str] = Field(None, description="Resource title")


class LTIContext(BaseModel):
    """LTI Context claim model."""
    id: str = Field(..., description="Context ID")
    label: Optional[str] = Field(None, description="Context label")
    title: Optional[str] = Field(None, description="Context title")
    type: Optional[List[str]] = Field(None, description="Context types")


class LTIToolPlatform(BaseModel):
    """LTI Tool Platform claim model."""
    guid: str = Field(..., description="Platform GUID")
    contact_email: Optional[str] = Field(None, description="Contact email")
    description: Optional[str] = Field(None, description="Platform description")
    name: Optional[str] = Field(None, description="Platform name")
    url: Optional[HttpUrl] = Field(None, description="Platform URL")
    product_family_code: Optional[str] = Field(None, description="Product family code")
    version: Optional[str] = Field(None, description="Platform version")


class LTILearningInformationServices(BaseModel):
    """LTI Learning Information Services claim model."""
    person_sourcedid: Optional[str] = Field(None, description="Person sourced ID")
    course_offering_sourcedid: Optional[str] = Field(None, description="Course offering sourced ID")
    course_section_sourcedid: Optional[str] = Field(None, description="Course section sourced ID")


class LTIMigration(BaseModel):
    """LTI Migration claim model."""
    oauth_consumer_key: str = Field(..., description="OAuth consumer key")
    oauth_consumer_key_sign: Optional[str] = Field(None, description="OAuth consumer key signature")
    user_id: Optional[str] = Field(None, description="User ID")


class LTIUser(BaseModel):
    """LTI User claim model."""
    sub: str = Field(..., description="User subject")
    name: Optional[str] = Field(None, description="User name")
    given_name: Optional[str] = Field(None, description="Given name")
    family_name: Optional[str] = Field(None, description="Family name")
    email: Optional[str] = Field(None, description="User email")
    picture: Optional[HttpUrl] = Field(None, description="User picture URL")


class LTIAssignmentsGradesData(BaseModel):
    """LTI Assignments and Grades Service data model."""
    scope: List[Literal[
        "https://purl.imsglobal.org/spec/lti-ags/scope/score",
        "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly",
        "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem",
        "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly",
    ]] = Field(..., description="Available scopes")
    lineitems: Optional[str] = Field(None, description="Line items endpoint")
    lineitem: Optional[str] = Field(None, description="Line item endpoint")


class LTINamesRolesData(BaseModel):
    """LTI Names and Roles Provisioning Service data model."""
    context_memberships_url: str = Field(..., description="Context memberships URL")
    service_versions: List[str] = Field(..., description="Service versions")


class LTICourseGroupsData(BaseModel):
    """LTI Course Groups Service data model."""
    context_groups_url: str = Field(..., description="Context groups URL")
    scope: List[str] = Field(..., description="Available scopes")


class LTIDeepLinkData(BaseModel):
    """LTI Deep Link data model."""
    deep_link_return_url: str = Field(..., description="Deep link return URL")
    accept_types: List[str] = Field(..., description="Accepted content types")
    accept_presentation_document_targets: List[str] = Field(..., description="Accepted presentation targets")
    accept_media_types: Optional[List[str]] = Field(None, description="Accepted media types")
    accept_data: Optional[List[str]] = Field(None, description="Accepted data types")


class LTILaunchData(BaseModel):
    """Complete LTI launch data model."""
    iss: str = Field(..., description="Issuer")
    sub: str = Field(..., description="Subject")
    aud: str = Field(..., description="Audience")
    exp: int = Field(..., description="Expiration time")
    iat: int = Field(..., description="Issued at time")
    nonce: str = Field(..., description="Nonce")
    azp: Optional[str] = Field(None, description="Authorized party")
    
    # LTI specific claims
    https_purl_imsglobal_org_spec_lti_claim_message_type: Optional[str] = Field(
        None, alias="https://purl.imsglobal.org/spec/lti/claim/message_type",
        description="LTI message type"
    )
    https_purl_imsglobal_org_spec_lti_claim_version: Optional[str] = Field(
        None, alias="https://purl.imsglobal.org/spec/lti/claim/version",
        description="LTI version"
    )
    https_purl_imsglobal_org_spec_lti_claim_deployment_id: Optional[str] = Field(
        None, alias="https://purl.imsglobal.org/spec/lti/claim/deployment_id",
        description="Deployment ID"
    )
    
    # Resource link
    https_purl_imsglobal_org_spec_lti_claim_resource_link: Optional[LTIResourceLink] = Field(
        None, alias="https://purl.imsglobal.org/spec/lti/claim/resource_link",
        description="Resource link information"
    )
    
    # Context
    https_purl_imsglobal_org_spec_lti_claim_context: Optional[LTIContext] = Field(
        None, alias="https://purl.imsglobal.org/spec/lti/claim/context",
        description="Context information"
    )
    
    # Tool platform
    https_purl_imsglobal_org_spec_lti_claim_tool_platform: Optional[LTIToolPlatform] = Field(
        None, alias="https://purl.imsglobal.org/spec/lti/claim/tool_platform",
        description="Tool platform information"
    )
    
    # User
    https_purl_imsglobal_org_spec_lti_claim_user: Optional[LTIUser] = Field(
        None, alias="https://purl.imsglobal.org/spec/lti/claim/user",
        description="User information"
    )
    
    # Services
    https_purl_imsglobal_org_spec_lti_ags_claim_endpoint: Optional[LTIAssignmentsGradesData] = Field(
        None, alias="https://purl.imsglobal.org/spec/lti/ags/claim/endpoint",
        description="Assignments and grades service"
    )
    
    https_purl_imsglobal_org_spec_lti_nrps_claim_namesroleservice: Optional[LTINamesRolesData] = Field(
        None, alias="https://purl.imsglobal.org/spec/lti/nrps/claim/namesroleservice",
        description="Names and roles service"
    )
    
    https_purl_imsglobal_org_spec_lti_gs_claim_groupsservice: Optional[LTICourseGroupsData] = Field(
        None, alias="https://purl.imsglobal.org/spec/lti/gs/claim/groupsservice",
        description="Course groups service"
    )
    
    # Deep linking
    https_purl_imsglobal_org_spec_lti_dl_claim_deep_linking_settings: Optional[LTIDeepLinkData] = Field(
        None, alias="https://purl.imsglobal.org/spec/lti/dl/claim/deep_linking_settings",
        description="Deep linking settings"
    )
    
    class Config:
        populate_by_name = True  # Pydantic V2 equivalent of allow_population_by_field_name
        extra = "allow"  # Allow additional fields that might be present
